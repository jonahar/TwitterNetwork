import time
import logging
from TwitterAPI import TwitterAPI
from lib.data_writer import DataWriter as DW

API_FIRST_PAGE = -1
RATE_LIMIT_CODE = 88
MAX_IDS_LIST = 100000  # this is only a soft max.


class Miner:
    """
    A Miner object can talk to twitter (via twitter's API), retrieve data and store it in a
    local database. The Miner actions are reflected in the database
    """

    'Construct a new Miner for retrieving data from Twitter'

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

    def _get_limit_info(self, resource):
        """
        :param resource: the resource to which you need to get rate limit information
        :return: a dictionary with the rate limit status
        """
        r = self.api.request('application/rate_limit_status', params={'resources': resource})
        r = r.json()
        if 'errors' in r:
            error = r['errors'][0]
            if error['code'] == RATE_LIMIT_CODE:
                time.sleep(60)
                return self._get_limit_info(resource)  # try again
            else:
                raise Exception(error['message'])
        return r

    def mine_user(self, screen_name):
        """
        retrieve details of a specific user according to its screen name.
        :param screen_name the screen_name of the user to retrieve
        :return:
        """
        r = self.api.request('users/show', params={'screen_name': screen_name})
        details = r.json()
        self.writer.write_user(details)
        # todo should return anything?

    def _mine_friends_followers(self, screen_name, log_title, resource, endpoint, limit,
                                writer_func):
        """
        retrieve ids of friends or followers
        :param screen_name:
        :return:
        """
        self.logger.info('mining {0} ids'.format(log_title))
        if limit == 0:
            limit = float('inf')
        ids = []
        total = 0  # total number of ids we retrieved so far
        page = API_FIRST_PAGE
        while total < limit:
            # todo maybe try to get the rate limit together with the response (should be found in the response header)
            r = self.api.request(endpoint,
                                 params={'screen_name': screen_name,
                                         'cursor': page})
            r = r.json()
            if 'errors' in r:
                error = r['errors'][0]
                if error['code'] == RATE_LIMIT_CODE:
                    # rate limit exceeded
                    rate_limit_info = self._get_limit_info(resource)
                    reset_time = rate_limit_info['resources'][resource][endpoint]['reset']
                    time_to_wait = reset_time - time.time()
                    time_to_wait *= 1.1  # just to be on the safe side, sleep 10% more than needed
                    time_to_wait = int(time_to_wait)
                    self.logger.info('Miner goes to sleep for {0} seconds'.format(time_to_wait))
                    time.sleep(time_to_wait)
                else:
                    # another, unrecognized error
                    raise Exception(error['message'])
                    # todo handle this error somehow instead of raising exception
            else:
                new_ids = r['ids']
                total_ids_to_add = min(len(new_ids), limit - total)  # how many ids we can
                # add without exceeding the limit
                new_ids = new_ids[:total_ids_to_add]
                ids += new_ids
                total += len(new_ids)
                # if we have many ids dump them to disk
                if len(ids) > MAX_IDS_LIST:
                    writer_func(self.writer, ids, screen_name)
                    ids = []
                page = r['next_cursor']
                if page == 0:
                    # no more pages
                    break
        writer_func(self.writer, ids, screen_name)
        # todo should return anything?

    def mine_followers_ids(self, screen_name=None, limit=0):
        """
        retrieve ids of the user's followers
        :param screen_name: the screen_name of the user
        :param limit: maximum number of followers to retrieve. default is 0 which means no limit
        :return:
        """
        return self._mine_friends_followers(screen_name, 'followers', 'followers',
                                            'followers/ids', limit, DW.write_followers)

    def mine_friends_ids(self, screen_name, limit=0):
        """
        retrieve ids of the user's friends
        :param screen_name: the screen_name of the user
        :param limit: maximum number of friends to retrieve. default is 0 which means no limit
        :return:
        """
        return self._mine_friends_followers(screen_name, 'friends', 'friends',
                                            'friends/ids', limit, DW.write_followers)
