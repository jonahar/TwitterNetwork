def get_tweet_chain_root(api, status):
    """
    :param api: tweepy API object
    :param status:
    :return: the id of the first status in the chain to which the given status belongs
    """
    print("status by", status.user.name)
    while status.in_reply_to_status_id is not None:
        # this is a reply to an older status
        status = api.get_status(status.in_reply_to_status_id, tweet_mode="extended")
        print("reply to", status.user.name)
    return status
