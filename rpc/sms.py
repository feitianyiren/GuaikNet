import logging
import requests
import json
from server.application import gm
rpc = gm.get("rpc")

api_key = "your_api_key"
api_secret = "your_secret"
brand = "Guaik"

@rpc.route()
def send_verify_code(number):
    request_id = None
    try:
        data = {"api_key":api_key,"api_secret":api_secret,"number":number,"brand":brand}
        headers = {'Content-Type': 'application/json'}
        r = requests.post("https://api.nexmo.com/verify/json",headers = headers, data = json.dumps(data))
        data = json.loads(r.text)
        if data["status"] == "0":
            request_id = data["request_id"]
    except Exception as e: logging.error(e)
    return request_id

@rpc.route()
def check_code(request_id,code):
    result = False
    try:
        data = {"api_key":api_key,"api_secret":api_secret,"request_id":request_id,"code":code}
        headers = {'Content-Type': 'application/json'}
        r = requests.post("https://api.nexmo.com/verify/check/json",headers = headers, data = json.dumps(data))
        data = json.loads(r.text)
        if data["status"] == "0":
            result = True
    except Exception as e: logging.error(e)
    return result
