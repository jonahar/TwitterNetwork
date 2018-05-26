def is_comment_retweet(t):
    """
    :param: t: tweet object (dictionary)
    :return: if the given tweet is a comment or a retweet of another tweet, return the screen_name
             of the author of the original tweet. otherwise, return None.
    """
    if t['in_reply_to_screen_name'] is not None:
        # this is a direct comment
        return t['in_reply_to_screen_name']
    if 'retweeted_status' in t:
        # this is a retweet with extra text (modification of the original tweet)
        return t['retweeted_status']['user']['screen_name']
    if 'quoted_status' in t:
        # this is an unmodified retweet
        return t['quoted_status']['user']['screen_name']
    return None
