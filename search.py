import json
from TwitterMine import test_toolbox
from TwitterAPI.TwitterPager import TwitterPager

miner = test_toolbox.get_miner()
api = miner.api


def search_comment_to_user(author_scr_name):
    """
    generator of tweets wwhich are replies to tweets by the given user
    :param author_scr_name:
    """
    q = 'to:' + author_scr_name
    r = TwitterPager(api, 'search/tweets', params={'q': q,
                                                   'tweet_mode': 'extended',
                                                   'count': 100})
    for t in r.get_iterator():
        yield t


def search_comments_to_tweet(tweet_id, author_scr_name):
    """
    generator of tweets which are replies for the given tweet

    :param tweet_id: tweet id of the tweet to which comments are searched
    :param author_scr_name: screen name of the tweet's author
    """
    q = 'to:' + author_scr_name
    r = TwitterPager(api, 'search/tweets', params={'q': q,
                                                   'sinceId': tweet_id,
                                                   'tweet_mode': 'extended',
                                                   'count': 100})
    for t in r.get_iterator():
        if t['in_reply_to_status_id'] == tweet_id:
            yield t


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


def download_users(term, max_tweets, min_retweets=0, min_likes=0):
    """
    download users whose tweets come up in the search of the given term
    (in case of a retweet also download original author)

    :param term: the search term
    :param max_tweets: maximum number of tweets to search (positive integer)
    :param min_retweets: consider only tweets that have at least this amount of retweets
    :param min_likes: consider only tweets that have at least this amount of likes
    :return: list of strings. each string is in the format "<user_id>;<screen_name>;<name>"
    """
    users = []
    count = 0
    for t in search_tweets(term, min_retweets, min_likes):
        users.append(user_repr(t['user']))
        # also get details of the original tweet author, if exist
        if 'retweeted_status' in t:
            users.append(user_repr(t['retweeted_status']['user']))
        elif 'quoted_status' in t:
            users.append(user_repr(t['quoted_status']['user']))
        count += 1
        if count > max_tweets:
            break
    return users


MIN_RETWEETS = 200
MIN_LIKES = 0
MAX_TWEETS = 100000

if __name__ == '__main__':
    term = '(israel OR zionist) (hamas OR gaza OR palestine) (fence OR crimes OR terror)'
    users = download_users(term, MAX_TWEETS, MIN_RETWEETS, MIN_LIKES)
    out_filename = 'israel-gaza.results'
    with open(out_filename, mode='a+') as f:
        f.writelines(users)
