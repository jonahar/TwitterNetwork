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

    def mine_user(self, user):
        """
        retrieve details of a specific user into the DB
        :param user: id or screen_name
        :return: the User object (tweepy.models.User) of the user that was mined
        """
        user = self.api.get_user(user)
        self.db.add_user((user.id, user.screen_name, user.name))
        return user

    def mine_friends_ids(self, user, limit=0):
        """
        get ids of this users' friends (people that the given user is following).
        This function does not return the result, but is reflected in the database.
        :param user: id or a screen_name of a user
        :param limit: int, maximum number of results to fetch from Twitter. 0 means no limit
        :return: total number of friends that were processed, i.e. retrieved from twitter. (if all
                 goes well this should return the limit, in case it was specified, otherwise should
                 return the total number of friends the user have)
        """
        # mine user details and add to the database
        user = self.mine_user(user)
        cursor = tweepy.Cursor(self.api.friends_ids, id=user.id)
        total_processed = 0
        for id in cursor.items(limit):
            total_processed += 1
            # add the id of the friend to the db
            self.db.add_user((id, '', ''))
            # add the pair to 'Follows'
            self.db.add_follows([user.id], [id])
        logging.info('Processed {0} friends of {1}'.format(total_processed, user.name))
        return total_processed

    def mine_followers_ids(self, user, limit=0):
        """
        get all the followers of the given user.
        This function does not return the result, but is reflected in the database.
        :param user: id or a screen_name of a user
        :param limit: int, maximum number of results to fetch from Twitter. 0 means no limit
        :return: total number of followers that were processed, i.e. retrieved from twitter. (if all
                 goes well this should return the limit, in case it was specified, otherwise should
                 return the total number of followers the user have)
        """
        # mine user details and add to the database
        user = self.mine_user(user)
        cursor = tweepy.Cursor(self.api.followers_ids, id=user.id)
        total_processed = 0
        for id in cursor.items(limit):
            total_processed += 1
            # add the id of the follower to the db
            self.db.add_user((id, '', ''))
            # add the pair to 'Follows'
            self.db.add_follows([id], [user.id])
        logging.info('Processed {0} followers of {1}'.format(total_processed, user.name))
        return total_processed

# todo total_processed is inaccurate. not necessarily all of them were added. some may have
# already exist
