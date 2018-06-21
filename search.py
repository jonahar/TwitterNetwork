from TwitterAPI.TwitterPager import TwitterPager
from TwitterMine import test_toolbox
from TwitterMine import utils

api = test_toolbox.get_app_api()


def get_tweet(tweet_id):
    r = api.request('statuses/lookup', params={'id': tweet_id})
    return r.json()


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


def search_tweets(term, min_retweets=0, min_likes=0, cond_type='and'):
    """
    Generator of tweets that match a search. tweets are filtered according to given parameters

    :param term: the term to search
    :param min_retweets: minimum number of times the tweet has been retweeted
    :param min_likes: minimum number of likes for the tweet
    :param cond_type: one of 'and' or 'or'. whether tweet have to satisfy both requirements, or just
                      once of them

    :return this is a generator, and as such it yields items
    """
    r = TwitterPager(api, 'search/tweets', params={'q': term,
                                                   'tweet_mode': 'extended',
                                                   'count': 100})
    for t in r.get_iterator():
        if cond_type == 'and':
            cond = t['favorite_count'] >= min_likes and t['retweet_count'] >= min_retweets
        else:
            cond = t['favorite_count'] >= min_likes or t['retweet_count'] >= min_retweets
        if cond:
            yield t


def result_repr(tweet, terms):
    """
    a minimal representation of a search result
    :param tweet:
    :param terms: list of terms to look for in the tweet

    :return: tweet_id;author_screen_name;original_author_scr_name;separated,matched,terms

             where original_author_scr_name is the screen name of the original author (in case of
             a retweet or a reply. ,may be empty) and separated,matched,terms are terms from the
             given list which exist in the tweet
    """
    author_scr_name = tweet['user']['screen_name']
    tweet_id = tweet['id_str']
    original_author_scr_name = utils.get_original_author(tweet)
    if original_author_scr_name is None:
        original_author_scr_name = ''
    text = utils.get_tweet_text(tweet).lower()
    matched_terms = ','.join([term for term in terms if term in text])

    return '{0};{1};{2};{3}'.format(tweet_id, author_scr_name, original_author_scr_name,
                                    matched_terms)


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


def download_users(search_query, out_filename, max_tweets, terms=(), min_retweets=0, min_likes=0):
    """
    download users whose tweets come up in the search of the given term
    (in case of a retweet also download original author).
    For each result, write a line to the output file, in the format specified in result_repr()

    :param search_query: the search term
    :param out_filename: output file to write results to
    :param max_tweets: maximum number of tweets to search (positive integer)
    :param terms: list of terms to look for in a result tweet (only affects the results
                  representation, but not the results themselves)
    :param min_retweets: consider only tweets that have at least this amount of retweets
    :param min_likes: consider only tweets that have at least this amount of likes
    :return: set of strings. each string is in the format specified in user_repr()
    """
    lines = []
    count = 0
    for t in search_tweets(search_query, min_retweets, min_likes, cond_type='or'):
        count += 1
        lines.append(result_repr(t, terms))
        if len(lines) >= MAX_USERS_LIST:
            print('covered', count, 'results')
            write_lines(lines, out_filename, append=True)
            lines = []
        if count >= max_tweets:
            break
    write_lines(lines, out_filename)


MIN_RETWEETS = 100
MIN_LIKES = 100
MAX_TWEETS = 100000

if __name__ == '__main__':
    terms = ['blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'ripple', 'bitcoin cash',
             'eos', 'litecoin', 'cardano', 'monero', 'zcash', 'iota']
    search_query = ' OR '.join(terms)
    out_filename = 'cryptocurrency-search-results'
    download_users(search_query, out_filename, MAX_TWEETS, terms, MIN_RETWEETS, MIN_LIKES)
