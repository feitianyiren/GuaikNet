import requests
import json

data = {"protocol":"json","version":"v1.01","action":"guaik.welcome","content":{}}
headers = {'Content-Type': 'application/json'}
r = requests.post("http://localhost:8080",headers = headers, data = json.dumps(data))
print r.text
