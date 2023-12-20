#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import json
import requests
import os
import sys

TOKEN_PATH_KEY = 'MCG_API_TOKEN_FILE'
TOKEN_KEY = 'MCG_API_TOKEN'

# Get MCG API Token or Token-File from OS environment
def get_api_token():
    if TOKEN_KEY in os.environ:
        return os.environ[TOKEN_KEY]
    elif TOKEN_PATH_KEY in os.environ:
        with open(os.environ[TOKEN_PATH_KEY], 'r') as f:
            return f.read().strip()
    else:
        raise "Missing token! Set either MCG_API_TOKEN or MCG_API_TOKEN_FILE in environment."

# Return (empty) JSON object 
def build_data():
    return json.dumps( { } ) 

def send_api_request(server_url):
    token = get_api_token()
    header = { 'Authorization': token,
               'Content-Type': 'application/json' }
    data = build_data()
    response = requests.get(url=server_url, headers=header)
    print(response.text)

if __name__ == '__main__':
    url = "https://api.premierheart.com/"
    if len(sys.argv) > 1:
        url = sys.argv[1]

    print("Connecting to unused endpoint. Should print 'ERROR /':")
    send_api_request(url)

