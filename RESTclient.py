import requests
import json

url = 'http://localhost:5000/todo/api/v1.0/tasks'
headers = {'content-type': 'application/json'}
data = json.dumps({'title': 'Task title', 'description': 'Task description'})


response = requests.post(url, data=data, headers=headers)
