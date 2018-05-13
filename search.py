import json
from TwitterMine import test_toolbox
from TwitterAPI.TwitterPager import TwitterPager

# search for important tweets (filter by number of retweets and likes), and write authors to file

NEWLINE = '\n'

miner = test_toolbox.get_miner()
api = miner.api
# SEARCH_TERM = 'iota (crypto OR cryptocurrency) -xrp'
SEARCH_TERM = 'bitcoin OR btc'
MIN_RETWEETS = 400
MIN_LIKES = 0
MAX_TWEETS = 10000


def search_tweets(term, min_retweets=0, min_likes=0):
    """
    Generator of tweets that match a search. tweets are filtered according to given parameters

    :param term: the term to search
    :param min_retweets: minimum number of times the tweet has been retweeted
    :param min_likes: minimum number of likes for the tweet

    :return this is a generator, and as such it yields items
    """
    r = TwitterPager(api, 'search/tweets', params={'q': term,
                                                   'tweet_mode': 'extended',
                                                   'count': 100})
    for t in r.get_iterator():
        if t['favorite_count'] >= min_likes and t['retweet_count'] >= min_retweets:
            yield t


def print_tweet_short(t):
    """
    Prints a short version of the tweet.
    Prints the author, text, and retweets/likes count

    :param t: tweet dictionary
    :return:
    """
    print('author: {0}({1})'.format(t['user']['name'], t['user']['screen_name']))
    print('retweet_count:', t['retweet_count'])
    print('favorite_count:', t['favorite_count'])
    if 'extended_tweet' in t:
        text = t['extended_tweet']['full_text']
    elif 'full_text' in t:
        text = t['full_text']
    else:
        text = t['text']
    print('text:', text)


def user_repr(user):
    """
    :param user: twitter user object (dictionary)
    :return: "<user_id>;<screen_name>;<name>"
    """
    return '{0};{1};{2}'.format(user['id'], user['screen_name'], user['name'])


out_filename = SEARCH_TERM + '.results'

with open(out_filename, mode='w') as outfile:
    count = 0
    for t in search_tweets(SEARCH_TERM, MIN_RETWEETS, MIN_LIKES):
        outfile.write(user_repr(t['user']))
        outfile.write(NEWLINE)
        if 'retweeted_status' in t:
            # also write details of the original tweet author
            outfile.write(user_repr(t['retweeted_status']['user']))
            outfile.write(NEWLINE)
        count += 1
        if count > MAX_TWEETS:
            break
