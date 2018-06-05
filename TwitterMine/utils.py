REG_TWEET = 0
RETWEET = 1
QUOTE = 2
REPLY = 3


def get_tweet_text(tweet):
    """
    :param tweet:
    :return: the text of this tweet
    """
    if 'extended_tweet' in tweet:
        text = tweet['extended_tweet']['full_text']
    elif 'full_text' in tweet:
        text = tweet['full_text']
    else:
        text = tweet['text']
    return text


def get_tweet_type(tweet):
    """
    :param tweet: tweet object 
    :return: the type of the given tweet. one of the constants above
    """
    if tweet['in_reply_to_screen_name'] is not None:
        return REPLY
    if 'quoted_status' in tweet:
        return QUOTE
    if 'retweeted_status' in tweet:
        return RETWEET

    return REG_TWEET


def get_original_author(t):
    """
    the screen name of the original author for this tweet.
    The original author is the user which is being retweeted, quoted, or replied to.
    If this tweet does not have an original author (i.e. this is a regular tweet), return None.

    :param: t: tweet object
    :return: the screen name of the original author for this tweet. The original author is the user
             which is being retweeted, quoted, or replied to. If this tweet does not have an
             original author (i.e. this is a regular tweet), return None.
    """
    type = get_tweet_type(t)
    if type == QUOTE:
        return t['quoted_status']['user']['screen_name']
    if type == RETWEET:
        return t['retweeted_status']['user']['screen_name']
    if type == REPLY:
        return t['in_reply_to_screen_name']

    return None
