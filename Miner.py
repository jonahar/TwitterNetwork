import tweepy
from DBManager import DBManager
import logging


class Miner:
    """
    A Miner object can talk to twitter (via twitter's API), retrieve data and store it in a
    local database. The Miner actions are reflected in the database
    """

    def __init__(self, keys, database_file):
        """
        Construct a new Miner for retrieving data from Twitter
        :param keys: dictionary with the needed keys (consumer_secret, consumer_token,
                                                        access_token, access_token_secret)
        :param database_file: string, filename of the database that the miner should work with.
        :param log_file: filename of log file.
        """
        self.db = DBManager(database_file)

        # establish connection to twitter API
        consumer_secret = keys["consumer_secret"]
        consumer_token = keys["consumer_token"]
        access_token = keys["access_token"]
        access_token_secret = keys["access_token_secret"]
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def mine_following_ids(self, user, limit=None):
        """
        get all the ids of users that the given user is following.
        This function does not return the result, but is reflected in the database.

        :param user: id or a screen_name of a user
        :param limit: int, maximum number of results to fetch from Twitter
        :return:
        """
        user = self.api.get_user(user)
        cursor = tweepy.Cursor(self.api.friends_ids, id=user.id)
        total_following = 0
        # todo fix this so we retrieve no more than limit results (cut at the middle of the page)
        for page in cursor.pages():
            # page is a list of ids
            self.db.add_follows([user.id], page)
            total_following += len(page)
            if limit is not None and total_following >= limit:
                break
        logging.info(
            'miner added {0} users being followed by {1}'.format(total_following, user.name))

    def mine_followers_ids(self, user, limit=None):
        """
        get all the followers of the given user.
        This function does not return the result, but is reflected in the database.

        :param user: id or a screen_name of a user
        :param limit: int, maximum number of results to fetch from Twitter
        :return:
        """
        user = self.api.get_user(user)
        cursor = tweepy.Cursor(self.api.followers_ids, id=user.id)
        total_followers = 0
        # todo fix this so we retrieve no more than limit results (cut at the middle of the page)
        for page in cursor.pages():
            # page is a list of ids
            self.db.add_follows(page, [user.id])
            total_followers += len(page)
            if limit is not None and total_followers >= limit:
                break
        logging.info("miner added {0} users that follows {1}".format(total_followers, user.name))

# todo total_following and total_followers numbers are inaccurate. not necessarily all of them
# were added. some may have already exist
