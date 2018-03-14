import requests
import json

url = 'http://localhost:5000/mine/following_ids/realJonaHarris'
headers = {'content-type': 'application/json'}
data = json.dumps({'user': 'realJonaHarris'})


response = requests.post(url, headers=headers)  # data=data,
