import requests
import json

headers = {'content-type': 'application/json'}

url = 'http://localhost:5000/mine/following_ids'
data = json.dumps({'user': 'realJonaHarris', 'limit': 5})

url = 'http://localhost:5000/mine/followers_ids'
data = json.dumps({'user': 'realDonaldTrump', 'limit': 20})

response = requests.post(url, data=data, headers=headers)

# see the results in the DB
from DBManager import DBManager

db = DBManager('/cs/usr/jonahar/PythonProjects/TwitterMine/DB/TwitterMineDB.db')
db.get_friends(attr='name')
