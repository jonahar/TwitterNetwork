import os
import json
import logging
from threading import Lock

NEWLINE = '\n'
# directory for writing stream tweets. prefix '#' is necessary so this dir will not be in conflict
# with a legal twitter screen name
STREAMS_TOP_DIR_NAME = '#streams'


class DataWriter:
    def __init__(self, data_dir):
        """
        :param data_dir: the main data directory
        """
        self.data_dir = data_dir
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
        self.streams_top_dir = os.path.join(self.data_dir, STREAMS_TOP_DIR_NAME)
        if not os.path.isdir(self.streams_top_dir):
            os.makedirs(self.streams_top_dir)
        self.logger = logging.getLogger()
        self.init_dir_lock = Lock()

    def _get_user_dir(self, scr_name):
        return os.path.join(self.data_dir, scr_name)

    def _init_user_dir(self, scr_name):
        """
        creates a directory for a user, if not already exist.
        the created directory will not contain any user information.
        this functions is used for when new data should be stored under this user (i.e. a tweet
        by this user was added, but user details weren't)

        :param scr_name: string, the screen name of the user
        :return: the user's directory full path
        """
        user_dir = self._get_user_dir(scr_name)
        self.init_dir_lock.acquire()  # two threads may try to write different data to the same
        # user at the same time
        if not os.path.isdir(user_dir):
            os.mkdir(user_dir)
        self.init_dir_lock.release()
        return user_dir

    def _init_stream_dir(self, stream_str):
        """
        creates a directory for a stream, if not already exists
        :return: the path of the stream directory
        """
        stream_dir = os.path.join(self.streams_top_dir, stream_str)
        if not os.path.isdir(stream_dir):
            os.mkdir(stream_dir)
        return stream_dir

    def user_details_exist(self, screen_name):
        """
        :return: True if the database contains the details of the given user
        """
        return os.path.isfile(os.path.join(self._get_user_dir(screen_name), 'user_details'))

    def write_user(self, details):
        """
        write user details from the given dictionary. If such user already has details file in the
        database, they will be override.
        :param details: dictionary with the details to write. must include at least one key 'id'
        """
        user_dir = self._init_user_dir(details['screen_name'])
        user_info_file = os.path.join(user_dir, 'user_details')
        # even if this file exist we override it with the new data
        data = json.dumps(details, indent=4, sort_keys=True)
        # self.logger.info('writing user details for {0}'.format(details['screen_name']))
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
        # self.logger.info('writing friends of {0}'.format(screen_name))
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
        # self.logger.info('writing followers of {0}'.format(screen_name))
        self._write_friends_followers(user_friends_file, followers_ids, append)

    def write_tweets_of_user(self, tweets, screen_name):
        """
        write list of tweets. each tweet is written in json format in a new line (no newline
        character in a tweet)
        :param tweets: list of dictionaries. each dictionary correspond to a single tweet by the user
        :param screen_name: the screen name of the user
        :return:
        """
        # self.logger.info('writing tweets')
        user_dir = self._init_user_dir(screen_name)
        tweets_file_path = os.path.join(user_dir, 'tweets')
        with open(tweets_file_path, 'a+') as f:
            for t in tweets:
                data = json.dumps(t).replace(NEWLINE, ' ')
                f.write(data)
                f.write(NEWLINE)

    def write_tweets_of_stream(self, tweets, stream_str):
        """
        writing to the database a set of tweets, which are related to some stream (for
        instance, tweets that were returned by twitter's Streaming API).

        All tweets coming from streams are written in files inside a directory #streams

        :param tweets: list of dictionaries. each dictionary correspond to a single tweet
        :param stream_str: a string representation of the stream. this is also the name of the file
        to which the tweets are written.
        """
        stream_dir = self._init_stream_dir(stream_str)  # e.g. data_dir/#streams/<stream_str>
        stream_file = os.path.join(stream_dir, 'tweets')
        with open(stream_file, 'a+') as f:
            for t in tweets:
                data = json.dumps(t).replace(NEWLINE, ' ')
                f.write(data)
                f.write(NEWLINE)

    def write_likes(self, tweets, screen_name):
        """
        write list of tweets that the user likes. each tweet is written in json format in a new
        line (no newline character in a tweet)
        :param tweets: list of dictionaries. each dictionary correspond to a single tweet that
                       the user likes
        :param screen_name: the screen name of the user
        :return:
        """
        # self.logger.info('writing likes')
        user_dir = self._init_user_dir(screen_name)
        tweets_file_path = os.path.join(user_dir, 'likes')
        with open(tweets_file_path, 'a+') as f:
            for t in tweets:
                data = json.dumps(t).replace(NEWLINE, ' ')
                f.write(data)
                f.write(NEWLINE)

    def write_neighbors(self, neighbors, screen_name):
        """
        :param neighbors: list of strings
        :param screen_name: the user to write neighbors to
        """
        user_dir = self._init_user_dir(screen_name)
        user_neighbors_file = os.path.join(user_dir, 'neighbors')
        with open(user_neighbors_file, mode='a+', encoding='utf-8') as f:
            for n in neighbors:
                f.write(n)
                f.write('\n')
