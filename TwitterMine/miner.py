import logging
from queue import Queue
from threading import Semaphore, Thread
from TwitterAPI import TwitterAPI, TwitterPager
from TwitterMine.data_writer import DataWriter as DW
from TwitterAPI.TwitterError import TwitterRequestError

RATE_LIMIT_CODE = 88
MAX_IDS_LIST = 100000
MAX_TWEETS_LIST = 500

JOBS_TYPES = ['user_details', 'friends_ids', 'followers_ids', 'tweets', 'likes']  # todo add listen


class Miner:
    """
    A Miner object can talk to twitter (via twitter's API), retrieve data and store it in a
    local database. The Miner actions are reflected in the database.

    The miner should be invoked by the method run(). The miner will then consist of
    multiple threads, each will handle a specific kind of job (each job has a different limit for
    using Twitter's API, so each thread will handle its job's limit). For each job type there is
    a special queue to which new jobs are inserted. A new job will appear in the queue in the form
    of a dictionary that consist of all needed arguments for this job.

    For more information about what arguments are needed for a specific job, look at the doc of its
    corresponding mine function, e.g. for adding new job for getting followers ids look
    at _mine_followers_ids()

    New jobs should be added only via the produce_job() function

    Each mining function related to some user will automatically mine the details of this user, so
    there is no need to call mine_user_details for users for which we perform other mining jobs.
    """

    def __init__(self, consumer_key, consumer_secret, data_dir):
        """
        Construct a new Miner for retrieving data from Twitter
        :param consumer_key:
        :param consumer_secret:
        :param data_dir: main directory to store the data
        """
        self.api = TwitterAPI(consumer_key, consumer_secret, auth_type='oAuth2')
        self.writer = DW(data_dir)
        self.logger = logging.getLogger()
        self.queues = {type: Queue() for type in JOBS_TYPES}
        # python queues are thread safe and don't require locks for multi-producers/consumers
        self.semaphores = {type: Semaphore(value=0) for type in JOBS_TYPES}
        # semaphore value starts from 0 because there are no jobs. at the first acquire by
        # the miner, the miner will be put to sleep

    def _mine_user_details(self, args):
        """
        retrieve details of a specific user according to its screen name.
        :param args: dictionary with a key 'screen_name' which indicates the user to retrieve
        :return:
        """
        screen_name = args['screen_name']
        self.logger.info('mining user details of {0}'.format(screen_name))
        r = self.api.request('users/show', params={'screen_name': screen_name})
        if r.status_code >= 400:
            logging.error('mining user details failed. Error code {0}'.format(r.status_code))
            return
        details = r.json()
        self.writer.write_user(details)

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
        :param title: 'friends' or 'followers'
        :param resource: the resource (e.g. 'followers/ids')
        :param writer_func: the writer's function to use
        :return:
        """
        # Unfortunately TwitterPager does not work with the ids methods.
        # Consider forking TwitterAPI
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
            pass  # error will be logged by TwitterRequestError's constructor

    def _mine_followers_ids(self, args):
        """
        retrieve ids of the user's followers
        :param args: dictionary with keys 'screen_name' and 'limit'. limit 0 means no limit
        :return:
        """
        self.logger.info('mining followers ids for user {0}'.format(args['screen_name']))
        return self._mine_friends_followers(args, 'followers/ids', DW.write_followers)

    def _mine_friends_ids(self, args):
        """
        retrieve ids of the user's friends
        :param args: dictionary with keys 'screen_name' and 'limit'. limit 0 means no limit
        :return:
        """
        self.logger.info('mining friends ids for user {0}'.format(args['screen_name']))
        return self._mine_friends_followers(args, 'friends/ids', DW.write_friends)

    def _mine_tweets_likes(self, args, resource, writer_func):
        """
        retrieve tweets or likes of a user
        :param args: dictionary with keys 'screen_name' and 'limit'
        :param resource: e.g. 'statuses/user_timeline'
        :param writer_func: the writer's function to use
        :return:
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
            pass  # error will be logged by TwitterRequestError's constructor

    def _mine_tweets(self, args):
        """
        retrieve tweets of the given user
        :param args: dictionary with keys 'screen_name' and 'limit'
        :return:
        """
        self.logger.info('mining tweets of user {0}'.format(args['screen_name']))
        return self._mine_tweets_likes(args, 'statuses/user_timeline', DW.write_tweets_of_user)

    def _mine_likes(self, args):
        """
        retrieve tweets that the user likes
        :param args: dictionary with keys 'screen_name' and 'limit'
        :return:
        """
        self.logger.info('mining likes of user {0}'.format(args['screen_name']))
        return self._mine_tweets_likes(args, 'favorites/list', DW.write_likes)

    def _run_consumer(self, job_type, job_func):
        """
        consume all jobs of a specific type. this function does not return and constantly handles or
        waiting for new jobs
        :param job_type: the type of job (one of the constants in miner.JOBS_TYPES)
        :param job_func: the miner function that should be called for handling this job
        :return:
        """
        while True:
            self.semaphores[job_type].acquire()
            job_args = self.queues[job_type].get()
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
        if job_type not in JOBS_TYPES:
            raise ValueError('Unsupported job type: "{0}"'.format(job_type))
        self.queues[job_type].put(args)
        self.semaphores[job_type].release()

    def run(self):
        """
        Start the miner.
        must be called before producing new jobs
        """
        # create thread for each different job type
        Thread(target=Miner._run_consumer,
               args=(self, 'followers_ids', Miner._mine_followers_ids)).start()

        Thread(target=Miner._run_consumer,
               args=(self, 'friends_ids', Miner._mine_friends_ids)).start()

        Thread(target=Miner._run_consumer,
               args=(self, 'tweets', Miner._mine_tweets)).start()

        Thread(target=Miner._run_consumer,
               args=(self, 'likes', Miner._mine_likes)).start()

        Thread(target=Miner._run_consumer,
               args=(self, 'user_details', Miner._mine_user_details)).start()

    def finish(self):
        """
        Finishes all jobs that were produced for the miner, and stop the miner.
        After calling this function new jobs should not be produced
        """
        for type in JOBS_TYPES:
            self.logger.info('Waiting for {0} jobs to finish'.format(type))
            self.queues[type].join()
