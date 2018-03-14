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

    def mine_connections_ids(self, user, type, limit):
        """
        retrieve followers or friends of a specific user.

        :param user: id or screen_name
        :param type: one of 'friends' or 'followers'
        :param limit: maximum number of results to retrieve, optional.
        :return: total number of connections processed (if all goes well this should return the
                 limit, in case it was specified, otherwise should return the total number of
                 followers/friends the user have)
        """
        if not limit:
            limit = float('inf')
        # get user details and add to the database
        user = self.api.get_user(user)
        self.db.add_user((user.id, user.screen_name, user.name))

        # realize what api function should we use
        if type == 'friends':
            api_func = self.api.friends_ids
        elif type == 'followers':
            api_func = self.api.followers_ids
        else:
            raise ValueError(
                'wrong value for argument "type" in function Miner.mine_connections_ids')

        # getting down to business
        cursor = tweepy.Cursor(api_func, id=user.id)
        total_processed = 0
        for page in cursor.pages():
            # page is a list of ids
            if total_processed + len(page) > limit:
                page = page[:limit - total_processed]
            # before adding pairs to 'Follows' add users to the 'Users' table
            for id in page:
                self.db.add_user((id, '', ''))  # add user with id only
            # add pairs. the order inside the pair is determined according to type
            if type == 'friends':
                self.db.add_follows([user.id], page)
            else:
                self.db.add_follows(page, [user.id])
            # update number of results we got so far and make sure we don't exceed it
            total_processed += len(page)
            if limit is not None and total_processed >= limit:
                break

        logging.info('Processed {0} '.format(total_processed) + type + ' of ' + user.name)
        return total_processed

    def mine_friends_ids(self, user, limit=None):
        """
        get ids of this users' friends (people that the given user is following).
        This function does not return the result, but is reflected in the database.

        :param user: id or a screen_name of a user
        :param limit: int, maximum number of results to fetch from Twitter
        :return:
        """
        self.mine_connections_ids(user, 'friends', limit)

    def mine_followers_ids(self, user, limit=None):
        """
        get all the followers of the given user.
        This function does not return the result, but is reflected in the database.

        :param user: id or a screen_name of a user
        :param limit: int, maximum number of results to fetch from Twitter
        :return:
        """
        self.mine_connections_ids(user, 'followers', limit)

    def mine_user(self, user):
        """
        retrieve details of a specific user into the DB
        :param user: id or screen_name
        :return:
        """
        user = self.api.get_user(user)
        self.db.add_user((user.id, user.screen_name, user.name))

# todo total_following and total_followers numbers are inaccurate. not necessarily all of them
# were added. some may have already exist
