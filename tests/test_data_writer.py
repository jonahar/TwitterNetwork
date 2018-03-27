import tests.bootstrap as boot
import logging


def write_data_multiple_users(screen_names, writer):
    """
    :param screen_names: list of screen names
    :return:
    """
    for name in screen_names:
        logging.getLogger().info('Processing user {0}'.format(name))

        r = api.request('statuses/user_timeline', params={'screen_name': name,
                                                          'count': 200,
                                                          'tweet_mode': 'extended'})
        tweets = r.json()  # list of dictionaries
        writer.write_tweets(tweets)

        r = api.request('followers/ids', params={'screen_name': name})
        followers = r.json()['ids']
        writer.write_followers(followers, name)

        r = api.request('friends/ids', params={'screen_name': name})
        friends = r.json()['ids']
        writer.write_friends(friends, name)


def tweets_different_authors(screen_names, writer):
    """
    :param screen_names: list of screen names
    :return:
    """
    # tweets by different authors
    tweets = []
    for name in screen_names:
        r = api.request('statuses/user_timeline',
                        params={'screen_name': name,
                                'count': 2,
                                'tweet_mode': 'extended'})
        tweets += r.json()
    writer.write_tweets(tweets)


api = boot.get_api()
writer = boot.get_api()

screen_names = ['realDonaldTrump', 'Google', 'DisneyPixar']
for name in screen_names:
    r = api.request('users/show', params={'screen_name': name})
    user_details = r.json()
    writer.write_user(user_details)

write_data_multiple_users(screen_names, writer)
# tweets_different_authors(screen_names, writer)
