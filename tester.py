import json
from miner import Miner

DB_FILE = '/cs/usr/jonahar/PythonProjects/TwitterMine/DB/TwitterMineDB.db'

ACCESS_TOKEN_FILENAME = "keys/access_token.json"
CONSUMER_TOKEN_FILENAME = "keys/consumer_token.json"

keys = dict()
with open(ACCESS_TOKEN_FILENAME) as a, open(CONSUMER_TOKEN_FILENAME) as c:
    keys.update(json.load(c))
    keys.update(json.load(a))

miner = Miner(keys, DB_FILE)

miner.get_following_ids('realDonaldTrump')
miner.get_following_ids('realJonaHarris')
miner.get_followers_ids('akkish007')  # some user with 9 followers
