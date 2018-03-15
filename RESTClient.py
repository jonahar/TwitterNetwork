import requests
import json
import logging
import sys

server_host_port = 'http://localhost:5000'
request_user_url = server_host_port + '/mine/user'
request_friends_url = server_host_port + '/mine/friends_ids'
request_followers_url = server_host_port + '/mine/followers_ids'

headers = {'content-type': 'application/json'}


def init_logger():
    # initialize logger
    logging.basicConfig(filename='client.log', level=logging.INFO,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S',
                        filemode='a')
    # print log messages to stdout too
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def request_user(user):
    data = json.dumps({'user': user})
    requests.post(request_user_url, data=data, headers=headers)


def request_friends(user, limit=0):
    data = json.dumps({'user': user, 'limit': limit})
    requests.post(request_friends_url, data=data, headers=headers)


def request_followers(user, limit=0):
    data = json.dumps({'user': user, 'limit': limit})
    requests.post(request_followers_url, data=data, headers=headers)


init_logger()

request_user('realDonaldTrump')
request_friends('realDonaldTrump')  # ~ 45
request_followers('realDonaldTrump', 20000)

request_user('nytimes')
request_friends('nytimes')  # ~ 880
request_followers('nytimes', 23000)

request_user('Google')
request_friends('Google')  # ~ 213

# Above operations should take 15 API calls. should be done quickly (no waiting)






# see the results in the DB
# from DBManager import DBManager
# db = DBManager('/cs/usr/jonahar/PythonProjects/TwitterMine/DB/TwitterMineDB.db')
# db.get_friends(attr='id')
