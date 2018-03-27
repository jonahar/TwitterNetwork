import time
from tests.bootstrap import boot


def get_limit_info(api, resources):
    """
    return a dictionary with the rate limit info about the different API endpoints
    :param api:
    :return:
    """
    r = api.request('application/rate_limit_status', params={'resources': resources})
    r = r.json()
    if 'errors' in r:
        raise Exception('Could not get rate limit information for Twitter')
    return r


def get_followers(api, screen_name, limit):
    """
    get friends of specific user
    :param screen_name:
    :param limit: maximum number of friends to get
    :return: list of friends' ids
    """
    next_page = -1  # -1 means the first page
    ids = []
    while len(ids) < limit:
        r = api.request('followers/ids',
                        params={'screen_name': screen_name, 'cursor': next_page})
        r = r.json()
        # todo check if got an error
        if 'errors' in r:
            if r['errors'][0]['code'] == 88:
                limit_info = get_limit_info(api, 'followers')

                # todo get the limit info, see how much time is left until reset and wait that time.
                # todo also check the api call for  application/rate_limit_status
                limit_info['resources']['followers']['followers/ids']

                # rate limit exceeded
                time.sleep(15 * 60)
            else:
                # another, unrecognized error
                raise Exception(
                    'Got error {0}: {1}'.format(r['errors'][0]['code'], r['errors'][0]['message']))
        new_ids = r['ids']
        if len(ids) + len(new_ids) > limit:
            new_ids = new_ids[:limit - len(ids)]
        ids += new_ids
        next_page = r['next_cursor']
        if next_page == 0:
            break  # no more friends
    return ids


api, writer = boot()
FOLLOWERS_LIMIT = 200000  # with chunks of 5000 friends, this should require 40 API
# calls, which means reaching the limit 2 times
friends = get_followers(api, 'realDonaldTrump', FOLLOWERS_LIMIT)

r = api.request('friends/ids', params={'screen_name': 'realJonaHarris', 'cursor': -1})
