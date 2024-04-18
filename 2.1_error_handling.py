#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import json
import requests
import os
import random
import sys
from datetime import datetime

TOKEN_PATH_KEY = 'MCG_API_TOKEN_FILE'
TOKEN_KEY = 'MCG_API_TOKEN'

def fake_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVcj9.EYjPC3mIoIjODhrWczovL3d3dy5wcmVtAwvYAgvHCNqUy29TiIWIC3viIjoiaHR0cHM6Ly9hcGkucHJlbWllcmhlYXJ0LmNvbSIsImF1ZCI6WyJodHRwczovL2FwaS5wcmVtaWVyaGVhcnQuY29tL2FwaSJdLCJleHAiOjI1MjQ2MDgwMDAsIm5iZiI6MTY4NjU4NTQzMCwiaWF0IjoxNjg2NTg1NDMwLCJqDgKIoJmSiMjSBci6mtiZndu2lCJzcHQiOjEyMzQ1Nn0=.YTc5MWRkN2JmZmQ1ZmM4YmZlMWVmMjNmMTRlYzRmYTE1YTRjOWYwYTY4MmY4Y2E5YTNkYzYyNzJiOTA4ODY4OA=="

def get_api_token():
    if TOKEN_KEY in os.environ:
        return os.environ[TOKEN_KEY]
    elif TOKEN_PATH_KEY in os.environ:
        with open(os.environ[TOKEN_PATH_KEY], 'r') as f:
            return f.read().strip()
    else:
        raise "Missing token! Set either MCG_API_TOKEN or MCG_API_TOKEN_FILE in environment."

def send_api_request(server_url, token, data):
    header = { 'Authorization': token,
               'Content-Type': 'application/json' }
    response = requests.post(url=server_url, headers=header, json=data)
    return response

def build_empty_request():
    return {
      "object-type": "analysis-request",
      "analysis": {
        "type": "mcg-aggregate",
        "options": {
          "diagnosis-matrix": True
        }
      },
      "output": {
        "report-json": {
        }
      },
      "input": [
      ]
    }

def random_data():
    return random.sample(range(0, (2**16-1)), (512*16))


def build_ecg_input():
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
      "type": "ecg",
      "format": "json",
      "timestamp": ts,
      "age": 40,
      "gender": "M",
      "data": {
        "frequency": 100,
        "signals": [
            {
            "name": "V5",
            "gain": 500.0,
            "offset": 0,
            "data": random_data(),
          },
          {
            "name": "II",                                                       
            "gain": 500.0,
            "offset": 0,
            "data": random_data(),
          }
        ]
      }
    }

def build_valid_request():
    req = build_empty_request()
    # add three 82-second recordings
    req['input'].append( build_ecg_input() )
    req['input'].append( build_ecg_input() )
    req['input'].append( build_ecg_input() )
    return req

def decode_error(resp):
    if resp.status_code != 200:
        return {
                "object-type": "http-error",
                "timestamp": str(datetime.now),
                "message": "Unknown error: HTTP %d" % resp.status_code
        }
    return json.loads(resp.text)

if __name__ == '__main__':
    url = "https://api.premierheart.com/api/v1/analyze"
    if len(sys.argv) > 1:
        url = sys.argv[1]

    token = None
    data = None

    print("[01] Connecting to invalid server")
    try:
        resp = send_api_request("http://192.254.254.254:11111/api/v1", token, data)
    except requests.exceptions.ConnectionError as e:
        print(" ... Caught exception")

    print("[02] Connecting to invalid path")
    bad_url = url + "-invalid"
    resp = send_api_request(bad_url, token, data)
    if resp.status_code == 401: print(" ... Caught 401 error")

    print("[03] Connecting with empty token")
    resp = send_api_request(url, token, data)
    if resp.status_code == 401: print(" ... Caught 401 error")

    print("[04] Connecting with invalid token")
    token = "XXXXXX"
    resp = send_api_request(url, token, data)
    if resp.status_code == 401: print(" ... Caught 401 error")

    print("[05] Connecting with bad/expired token")
    token = fake_token()
    resp = send_api_request(url, token, data)
    if resp.status_code == 401: print(" ... Caught 401 error")

    token = get_api_token()

    print("[06] Connecting with valid token and empty request")
    data = { }
    resp = send_api_request(url, token, data)
    h_err = decode_error(resp)
    if h_err['object-type'] == 'error':
        print(" ... Caught error '%s': %s " % (h_err['message'], h_err['details']))

    print("[07] Connecting with valid token and incorrect type")
    data = { 'object-type' : 'MyBrokenType', 'analysis' : { }, 'output' : { } }
    resp = send_api_request(url, token, data)
    h_err = decode_error(resp)
    if h_err['object-type'] == 'error':
        print(" ... Caught error '%s': %s " % (h_err['message'], h_err['details']))

    print("[08] Connecting with valid token and invalid request")
    data = { 'object-type' : 'analysis-request', 'analysis' : { }, 'output' : { } }
    resp = send_api_request(url, token, data)
    h_err = decode_error(resp)
    if h_err['object-type'] == 'error':
        print(" ... Caught error '%s': %s " % (h_err['message'], h_err['details']))

    print("[09] Connecting with valid token and empty request input")
    data = build_empty_request()
    resp = send_api_request(url, token, data)
    h_err = decode_error(resp)
    if h_err['object-type'] == 'error':
        print(" ... Caught error '%s': %s " % (h_err['message'], h_err['details']))

    print("[10] Connecting with valid token and invalid request input")
    data = { 'object-type' : 'MyBrokenType', 'analysis' : 'mcg-aggregate',
            'input' : 1.65, 'output' : { } }
    resp = send_api_request(url, token, data)
    h_err = decode_error(resp)
    if h_err['object-type'] == 'error':
        print(" ... Caught error '%s': %s " % (h_err['message'], h_err['details']))

    print("[11] Connecting with valid token and invalid analysis type")
    data = build_valid_request()
    data["analysis"]["type"] = "mcg-invalid"
    resp = send_api_request(url, token, data)
    h_err = decode_error(resp)
    if h_err['object-type'] == 'error':
        print(" ... Caught error: " + h_err['message'])


