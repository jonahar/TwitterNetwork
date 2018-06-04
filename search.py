from TwitterAPI.TwitterPager import TwitterPager
from TwitterMine import test_toolbox

api = test_toolbox.get_api()


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


def user_repr(tweet):
    """
    a minimal representation of the author of this tweet
    :param tweet: tweet object
    :return: "<user_id>;<screen_name>;<name>;<retweet_count>"
    """
    return '{0};{1};{2};{3}'.format(tweet['user']['id'], tweet['user']['screen_name'],
                                    tweet['user']['name'], tweet['retweet_count'])


def write_lines(lines, filename, append=True):
    """
    write strings in the given list to the file specified by filename. adds a newline after each
    string
    """
    mode = 'a+' if append else 'w'
    with open(filename, mode=mode, encoding='utf-8') as f:
        for line in lines:
            f.write(line)
            f.write('\n')


MAX_USERS_LIST = 1000


def download_users(term, out_filename, max_tweets, min_retweets=0, min_likes=0):
    """
    download users whose tweets come up in the search of the given term
    (in case of a retweet also download original author)

    :param term: the search term
    :param out_filename: output file to write results to
    :param max_tweets: maximum number of tweets to search (positive integer)
    :param min_retweets: consider only tweets that have at least this amount of retweets
    :param min_likes: consider only tweets that have at least this amount of likes
    :return: set of strings. each string is in the format specified in user_repr()
    """
    lines = set()
    count = 0
    for t in search_tweets(term, min_retweets, min_likes):
        lines.add(user_repr(t))
        # also get details of the original tweet author, if exist
        if 'retweeted_status' in t:
            lines.add(user_repr(t['retweeted_status']))
        elif 'quoted_status' in t:
            lines.add(user_repr(t['quoted_status']))

        if len(lines) >= MAX_USERS_LIST:
            write_lines(lines, out_filename, append=False)  # write each time to see partial results
        count += 1
        if count > max_tweets:
            break
    write_lines(lines, out_filename)
    return lines


MIN_RETWEETS = 200
MIN_LIKES = 0
MAX_TWEETS = 100000

if __name__ == '__main__':
    term = '(israel OR zionist) (hamas OR gaza OR palestine) (fence OR crimes OR terror)'
    out_filename = 'israel-gaza.results'
    download_users(term, out_filename, MAX_TWEETS, MIN_RETWEETS, MIN_LIKES)
