import os
import json
import logging

USER_DETAILS_KEYS = ['id', 'screen_name', 'name', 'friends_count', 'followers_count',
                     'statuses_count', 'created_at', 'favourites_count']
TWEET_KEYS = ['id', 'in_reply_to_status_id', 'in_reply_to_user_id', 'created_at']
NEWLINE = '\n'


class DataWriter:
    def __init__(self, data_dir):
        """
        :param data_dir: the main data directory
        """
        self.data_dir = data_dir
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
        self.logger = logging.getLogger()

    def _get_user_dir(self, scr_name):
        return os.path.join(self.data_dir, scr_name)

    def _init_user_dir(self, scr_name):
        """
        creates a directory for a user, if not already exist.
        the created directory will not contain any user information.
        this functions is used for when new data should be stored under this user (i.e. a tweet
        by this user was added, but user details weren't)

        :param id: string, id of the new user
        :return: the user's directory full path
        """
        user_dir = self._get_user_dir(scr_name)
        if not os.path.isdir(user_dir):
            os.mkdir(user_dir)
        return user_dir

    def write_user(self, details):
        """
        write user details from the given dictionary. If such user already has details file in the
        database, they will be override.
        :param details: dictionary with the details to write. must include at least one key 'id'
        """
        user_dir = self._init_user_dir(details['screen_name'])
        user_info_file = os.path.join(user_dir, 'user_details')
        # even if this file exist we override it with the new data
        data = {key: details[key] for key in USER_DETAILS_KEYS}
        data = json.dumps(data)
        self.logger.info('writing user details')
        with open(user_info_file, mode='w+') as f:
            f.write(data)

    def _write_friends_followers(self, file, ids, append):
        """
        write the ids in the ids list to the given file, opened according to the append parameter
        """
        mode = 'a+' if append else 'w+'
        with open(file, mode=mode) as f:
            for id in ids:
                f.write(str(id))
                f.write(NEWLINE)

    def write_friends(self, friends_ids, screen_name, append=True):
        """
        :param friends_ids: list of ids
        :param screen_name: the screen_name of the user to which the data relates
        :param append: whether the given list of friends should be appended to the existing list or
                       replace it.
        :return:
        """
        user_dir = self._init_user_dir(screen_name)
        user_friends_file = os.path.join(user_dir, 'friends')
        self.logger.info('writing user\'s friends')
        self._write_friends_followers(user_friends_file, friends_ids, append)

    def write_followers(self, followers_ids, screen_name, append=True):
        """
        :param followers_ids: list of ids
        :param screen_name: the screen name of the user to which the data relates
        :param append: whether the given list of followers should be appended to the existing list
                       or replace it.
        :return:
        """
        user_dir = self._init_user_dir(screen_name)
        user_friends_file = os.path.join(user_dir, 'followers')
        self.logger.info('writing user\'s followers')
        self._write_friends_followers(user_friends_file, followers_ids, append)

    def _parse_tweet_data(self, tweet):
        """
        create the dictionary that will be written for this tweet
        :param tweet: tweet dictionary
        :return the dictionary representing the tweet
        """
        # todo maybe should reformat the date attribute to something more convenient to work with
        data = {key: tweet[key] for key in TWEET_KEYS}
        if 'extended_tweet' in tweet:  # complies to the streaming API
            text = tweet['extended_tweet']['full_text']
        elif 'full_text' in tweet:
            text = tweet['full_text']
        else:
            text = tweet['text']
        text = text.replace(NEWLINE, ' ')
        data['text'] = text
        data['author_id'] = tweet['user']['screen_name']
        return data

    def write_tweets(self, tweets):
        """
        write list of tweets
        :param tweets: list of dictionaries. each dictionary correspond to a single tweet
        :return:
        """
        self.logger.info('writing tweets')
        opened_files = dict()
        for tweet in tweets:
            data = self._parse_tweet_data(tweet)
            # if tweets file of this user is already opened, use it
            author_id = data['author_id']
            data = json.dumps(data)
            author_dir = self._init_user_dir(str(author_id))
            if author_id not in opened_files:
                tweets_file_path = os.path.join(author_dir, 'tweets')
                opened_files[author_id] = open(tweets_file_path, mode='a')
            opened_files[author_id].write(data)
            opened_files[author_id].write(NEWLINE)
        for id in opened_files:
            opened_files[id].close()
