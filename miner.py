import tweepy
from DB import DB


class Miner:
    """
    A Miner object can talk to twitter (via twitter's API), retrieve data and store it in a
    local database. The Miner actions are reflected in the database
    """

    def __init__(self, keys, database_file):
        """
        Construct a new Miner for retrieving data from Twitter
        :param keys: dictionary with the needed keys (consumer_secret, consumer_token.json,
                                                        access_token.json, access_token_secret)
        :param database_file: string, filename of the database that the miner should work with.
        """
        self.db = DB(database_file)

        # make connection to twitter API
        consumer_secret = keys["consumer_secret"]
        consumer_token = keys["consumer_token"]
        access_token = keys["access_token"]
        access_token_secret = keys["access_token_secret"]
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def get_following_ids(self, user):
        """
        get all the ids of users that the given user is following.
        This function does not return the result, but is reflected in the database.

        :param user: id or a screen_name of a user
        :return:
        """
        user = self.api.get_user(user)
        cursor = tweepy.Cursor(self.api.friends_ids, id=user.id)
        total_following = 0
        for page in cursor.pages():
            # page is a list of ids
            self.db.add_follows([user.id], page)
            total_following += len(page)
        print("Added {0} users being followed by {1}".format(total_following, user.name))

    def get_followers_ids(self, user):
        """
        get all the followers of the given user.
        This function does not return the result, but is reflected in the database.

        :param user: id or a screen_name of a user
        :return:
        """
        user = self.api.get_user(user)
        cursor = tweepy.Cursor(self.api.followers_ids, id=user.id)
        total_followers = 0
        for page in cursor.pages():
            # page is a list of ids
            self.db.add_follows(page, [user.id])
            total_followers += len(page)
        print("Added {0} users that follows {1}".format(total_followers, user.name))
