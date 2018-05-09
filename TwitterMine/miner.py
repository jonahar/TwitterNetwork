import logging
import time
from queue import Queue
from threading import Thread
from TwitterAPI.TwitterAPI import TwitterAPI
from TwitterAPI.TwitterPager import TwitterPager
from TwitterMine.data_writer import DataWriter as DW
from TwitterAPI.TwitterError import TwitterRequestError, TwitterConnectionError

MAX_IDS_LIST = 100000
MAX_TWEETS_LIST = 500
STOP_SIGNAL = None  # this is a sign to all miner threads to stop

JOBS_TYPES = ['user_details', 'friends_ids', 'followers_ids', 'tweets', 'likes', 'listen']

FILTER_LEVEL = 'none'  # 'none' || 'low' || 'medium', to control the rate of incoming tweets


class Miner:
    """
    A Miner object can talk to twitter (via twitter's API), retrieve data and store it in a
    local database. The Miner actions are reflected in the database.

    The miner should be invoked by the method run(). The miner will then consist of
    multiple threads, each will handle a specific kind of job (each job has a different limit for
    using Twitter's API, so each thread will handle its job's limit). For each job type there is
    a special queue to which new jobs are inserted. A new job will appear in the queue in the form
    of a dictionary that consist of all needed arguments for this job.

    To properly close the miner (finish all its current jobs and writes) call the finish() method.

    For more information about what arguments are needed for a specific job, look at the doc of its
    corresponding mine function, e.g. to add new job for getting followers ids look
    at _mine_followers_ids()

    New jobs should be added only via the produce_job() function

    Each mining function related to some user will automatically mine the details of this user, so
    there is no need to call mine_user_details for users for which we perform other mining jobs.
    """

    def __init__(self, consumer_key, consumer_secret,
                 access_token_key, access_token_secret, data_dir):
        """
        Construct a new Miner for retrieving data from Twitter
        :param consumer_key:
        :param consumer_secret:
        :param access_token_key:
        :param access_token_secret:
        :param data_dir: main directory to store the data
        """
        self.api = TwitterAPI(consumer_key, consumer_secret,
                              access_token_key, access_token_secret)
        self.writer = DW(data_dir)
        self.logger = logging.getLogger()
        self.queues = {type: Queue() for type in JOBS_TYPES}
        # python queues are thread safe and don't require locks for multi-producers/consumers

        # create thread for each different job type
        self.threads = [
            Thread(target=Miner._run_consumer,
                   args=(self, 'followers_ids', Miner._mine_followers_ids)),
            Thread(target=Miner._run_consumer,
                   args=(self, 'friends_ids', Miner._mine_friends_ids)),
            Thread(target=Miner._run_consumer,
                   args=(self, 'tweets', Miner._mine_tweets)),
            Thread(target=Miner._run_consumer,
                   args=(self, 'likes', Miner._mine_likes)),
            Thread(target=Miner._run_consumer,
                   args=(self, 'user_details', Miner._mine_user_details)),
            Thread(target=Miner._run_consumer,
                   args=(self, 'listen', Miner._listen))]

        assert (len(JOBS_TYPES) == len(self.threads))  # one thread per job type

    def _mine_user_details(self, args):
        """
        retrieve details of a specific user according to its screen name.
        :param args: dictionary with a key 'screen_name' which indicates the user to retrieve
        :return: the id (integer) of the user
        """
        screen_name = args['screen_name']
        self.logger.info('mining user details of {0}'.format(screen_name))
        time.sleep(1)  # one request per second will avoid rate limit
        try:
            r = self.api.request('users/show', params={'screen_name': screen_name})
            if r.status_code >= 400:
                try:
                    msg = r.json()['errors'][0]['message']
                    self.logger.error('mining user details failed. {0}'.format(msg))
                except ValueError:
                    # response body does not contain valid json
                    self.logger.error(
                        'mining user details failed. Error code {0}'.format(r.status_code))
                return
            details = r.json()
            self.writer.write_user(details)
            self.logger.info('user details mined successfully')
            return details['id']
        except TwitterConnectionError as e:
            # message is logged the TwitterConnectionError constructor
            return None

    # todo implement mine function for users/lookup (retrieve multiple users details)

    def _produce_user_details_job(self, screen_name):
        """
        produce a new user_details job, if the details don't already exist.
        this function is called by other mining functions.
        """
        if not self.writer.user_details_exist(screen_name):
            self.produce_job('user_details', {'screen_name': screen_name})

    def _mine_friends_followers(self, args, resource, writer_func):
        """
        retrieve ids of friends or followers
        :param args: dictionary with the screen_name and limit
        :param resource: the resource ('followers/ids' or 'friends/ids')
        :param writer_func: the writer's function to use
        :return: True on a successful mining. False on error
        """
        screen_name = args['screen_name']
        limit = args['limit']
        self._produce_user_details_job(screen_name)
        if limit == 0:
            limit = float('inf')
        ids = []
        total = 0  # total number of ids we retrieved so far
        r = TwitterPager(self.api, resource, params={'screen_name': screen_name})
        try:
            for id in r.get_iterator():
                ids.append(id)
                total += 1
                if len(ids) > MAX_IDS_LIST:
                    writer_func(self.writer, ids, screen_name)
                    ids = []
                if total >= limit:
                    break
            writer_func(self.writer, ids, screen_name)
        except TwitterRequestError:
            # error will be logged by TwitterRequestError's constructor
            return False
        return True

    def _mine_followers_ids(self, args):
        """
        retrieve ids of the user's followers
        :param args: dictionary with keys 'screen_name' and 'limit'. limit 0 means no limit
        :return:
        """
        self.logger.info('mining followers ids for user {0}'.format(args['screen_name']))
        if not self._mine_friends_followers(args, 'followers/ids', DW.write_followers):
            self.logger.error('mining followers failed')
        else:
            self.logger.info('followers mined successfully')

    def _mine_friends_ids(self, args):
        """
        retrieve ids of the user's friends
        :param args: dictionary with keys 'screen_name' and 'limit'. limit 0 means no limit
        :return:
        """
        self.logger.info('mining friends ids for user {0}'.format(args['screen_name']))
        if not self._mine_friends_followers(args, 'friends/ids', DW.write_friends):
            self.logger.error('mining friends failed')
        else:
            self.logger.info('friends mined successfully')

    def _mine_tweets_likes(self, args, resource, writer_func):
        """
        retrieve tweets or likes of a user
        :param args: dictionary with keys 'screen_name' and 'limit'
        :param resource: 'statuses/user_timeline' or 'favorites/list'
        :param writer_func: the writer's function to use
        :return: True if mining ended successfully
        """
        screen_name = args['screen_name']
        limit = args['limit']
        self._produce_user_details_job(screen_name)
        if limit == 0:
            limit = float('inf')
        tweets = []
        total = 0
        r = TwitterPager(self.api, resource, params={'screen_name': screen_name,
                                                     'count': 200,
                                                     'tweet_mode': 'extended'})
        try:
            for t in r.get_iterator():
                tweets.append(t)
                total += 1
                if len(tweets) > MAX_TWEETS_LIST:
                    writer_func(self.writer, tweets, screen_name)
                    tweets = []
                if total >= limit:
                    break
            writer_func(self.writer, tweets, screen_name)
        except TwitterRequestError:
            # error will be logged by TwitterRequestError's constructor
            return False
        return True

    def _mine_tweets(self, args):
        """
        retrieve tweets of the given user
        :param args: dictionary with keys 'screen_name' and 'limit'
        :return:
        """
        self.logger.info('mining tweets of user {0}'.format(args['screen_name']))
        if not self._mine_tweets_likes(args, 'statuses/user_timeline', DW.write_tweets_of_user):
            self.logger.error('mining tweets failed')
        else:
            self.logger.info('tweets mined successfully')

    def _mine_likes(self, args):
        """
        retrieve tweets that the user likes
        :param args: dictionary with keys 'screen_name' and 'limit'
        :return:
        """
        self.logger.info('mining likes of user {0}'.format(args['screen_name']))
        if not self._mine_tweets_likes(args, 'favorites/list', DW.write_likes):
            self.logger.error('mining likes failed')
        else:
            self.logger.info('likes mined successfully')

    def _update_listen_parameters(self, track, follow, args):
        """
        update the current listen parameters (track and follow) according to the given args
        :param track: set
        :param follow: set
        :param args: args dictionary to the listen job
        :return: a tuple (track, follow) - the updated sets
        """
        if args['mode'] == 'add':
            if 'track' in args:
                track = track.union(args['track'])
            if 'follow' in args:
                follow = follow.union(args['follow'])
        elif args['mode'] == 'remove':
            if 'track' in args:
                track = track.difference(args['track'])
            if 'follow' in args:
                follow = follow.difference(args['follow'])
        return track, follow

    def _get_listen_query_representation(self, track, follow):
        """
        return a unique string representation for a twitter's listen request. representation depends
        on the request arguments track and follow
        :param track: set of strings
        :param follow: set of strings
        :return: string - representation of the listen request
        """
        keywords = [term for term in track] + [term for term in follow]
        keywords.sort()
        return '.'.join(keywords)

    def _listen(self):
        """
        this function handles all listen jobs.
        the args to a listen job is a dictionary with the following structure
             {'mode'   : 'add' / 'remove',
              'track'  : ['term1', 'term2', ... ],
              'follow' : ['id1', 'id2', ... ] }

        :return: this function does not return
        """
        track = set()
        follow = set()
        args_queue = self.queues['listen']
        while True:
            try:
                while (not args_queue.empty()) or (not track and not follow):
                    # there are more arguments to process OR both track and follow are empty
                    args = args_queue.get(block=True, timeout=None)  # will block if queue is empty
                    if args is STOP_SIGNAL:
                        return
                    args_queue.task_done()
                    track, follow = self._update_listen_parameters(track, follow, args)
                self.logger.info(
                    'listening: track={0}, follow={1}'.format(str(track), str(follow)))
                r = self.api.request('statuses/filter', {'track': ','.join(track),
                                                         'follow': ','.join(follow),
                                                         'tweet_mode': 'extended',
                                                         'stall_warnings': 'true',
                                                         'filter_level': FILTER_LEVEL})
                stream_str = self._get_listen_query_representation(track, follow)  # the string
                # representation of the stream
                iterator = r.get_iterator()
                for item in iterator:
                    if item:
                        if 'warning' in item:
                            self.logger.warning(item['warning']['message'])
                        elif 'disconnect' in item:
                            event = item['disconnect']
                            self.logger.error('streaming API shutdown: {0}'.format(event['reason']))
                            break
                        elif 'text' in item or 'full_text' in item or 'extended_tweet' in item:
                            # item is a tweet. ready to be written
                            self.writer.write_tweets_of_stream([item], stream_str)

                        # currently, no use in the following types of messages
                        elif 'delete' in item:
                            # user deleted a tweet
                            tweet = item['status']
                            pass
                        elif 'limit' in item:
                            # more Tweets were matched than the current rate limit allows
                            pass
                        elif 'event' in item and item['event'] == 'user_update':
                            # user updated his profile
                            pass

                    if not args_queue.empty():
                        # new job args received. close current connection, update args and
                        # start again
                        r.close()
                        break

            except TwitterRequestError as e:
                if e.status_code < 500:
                    # something needs to be fixed before re-connecting
                    raise
                else:
                    # temporary interruption, re-try request
                    pass
            except TwitterConnectionError:
                # temporary interruption, re-try request
                pass

    def _run_consumer(self, job_type, job_func):
        """
        consume all jobs of a specific type. this function does not return and constantly handles or
        waiting for new jobs
        :param job_type: the type of job (one of the constants in miner.JOBS_TYPES)
        :param job_func: the miner function that should be called for handling this job
        :return:
        """
        if job_type == 'listen':
            job_func(self)
        else:  # standard rest API job
            while True:
                job_args = self.queues[job_type].get(block=True,
                                                     timeout=None)
                if job_args is STOP_SIGNAL:
                    return
                # if no job available, get() will block until new job arrives
                job_func(self, job_args)
                self.queues[job_type].task_done()  # this is to indicate that the job was processed.
                # this is important if anyone wants to wait until all jobs in the queue are done

    def produce_job(self, job_type, args):
        """
        Create a new job to be handles by the miner.
        :param job_type: the job to perform. one of the constants in miner.JOBS_TYPES
        :param args: dictionary with the needed arguments for this job
        :return:
        """
        if args is STOP_SIGNAL:
            self.logger.error('invalid job arguments to "{0}"'.format(job_type))
        if job_type not in JOBS_TYPES:
            raise ValueError('Unsupported job type: "{0}"'.format(job_type))
        self.queues[job_type].put(args)

    def run(self):
        """
        Start the miner.
        must be called before producing new jobs
        """
        for t in self.threads:
            t.start()

    def stop(self):
        """
        Finishes all jobs that were produced for the miner, and stop the miner.
        After calling this function new jobs should not be produced
        """
        self.logger.info('notify all miner threads to stop')
        for type in JOBS_TYPES:
            self.queues[type].put(STOP_SIGNAL)
        self.logger.info('wait for all miner threads to stop')
        for t in self.threads:
            t.join()
        self.logger.info('miner stopped')
