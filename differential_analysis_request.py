#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import base64
import json
import requests
import io
import os
import random
import sys
from datetime import datetime
import pandas as pd

TOKEN_PATH_KEY = 'MCG_API_TOKEN_FILE'
TOKEN_KEY = 'MCG_API_TOKEN'

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

def build_request(inputs):
    return {
      "object-type": "analysis-request",
      "analysis": {
        "type": "mcg-differential",
        "options": { }
      },
      "output": {
        "result-diff-csv": {
            'delimiter': '|'
        },
        "result-json": {
            'in-place-json': True
        },
        "transform-heatmap": {
        },
        "transform-json": {
            'in-place-json': True
        }
      },
      "input": inputs,
      "comment": "(FAKE DATA) Generated by " + os.path.basename(__file__)
    }

def input_for_ecg_json(json_str, age=40, gender='M'):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
      "type": "ecg",
      "format": "json",
      "timestamp": ts,
      "age": age,
      "gender": gender,
      "data": json.loads(json_str)
    }

def decode_response(resp):
    if resp.status_code != 200:
        return {
                "object-type": "http-error",
                "timestamp": str(datetime.now),
                "message": "Unknown error: HTTP %d" % resp.status_code
        }
    return json.loads(resp.text)

def print_results_summary(res, indent="\t"):
    if 'comment' in res:
        print(indent + "Comment: " + res['comment'])

    print(indent + "Tracing Quality:")
    for fname, score in res['tracing-quality'].items():
        print(indent + indent + "%s : %d" % (fname, score))

    print(indent + "ECG Details:")
    for fname, lead_stats in res['ecg-stats'].items():
        print(indent + indent + fname)
        for lead, h in lead_stats.items():
            print(indent + indent + indent + "%s  Count: %d  High: %d  Low: %d  Baseline: %d  Total: %d  Peak Count: %d  Voltage: %0.2f  PPV: %d" % (lead, h['count'], h['high'], h['low'], h['baseline'], h['total'], h['peak_count'], h['voltage'], h['ppv']))


if __name__ == '__main__':
    url = "https://api.premierheart.com/api/v1/analyze"
    if len(sys.argv) > 1:
        url = sys.argv[1]

    inputs = [ ]
    for x in range(5):
        fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', ("ecg_pre_%d.json" % (x+1)))
        with open(fname, 'r') as f:
            h_input = input_for_ecg_json(f.read())
            h_input['name'] = os.path.splitext(os.path.basename(fname))[0]
            h_input['group'] = 'pre'
            inputs.append(h_input)
        print("Read input: %s" % (fname))
    for x in range(3):
        fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', ("ecg_post_%d.json" % (x+1)))
        with open(fname, 'r') as f:
            h_input = input_for_ecg_json(f.read())
            h_input['name'] = os.path.splitext(os.path.basename(fname))[0]
            h_input['group'] = 'post'
            inputs.append(h_input)
        print("Read input: %s" % (fname))

    token = get_api_token()
    data = build_request( inputs )
    resp = send_api_request(url, token, data)
    results = decode_response(resp)

    if results['object-type'] != 'analysis-result':
        print("Unexpected return value from API server:")
        for k,v in results.items():
            print("\t%s: %s" % (k, v))
        sys.exit()

    # save to disk:
    with open("analysis-results.ecg-files.example.json", 'w') as f:
        f.write(json.dumps(results))

    print("Results Summary:")
    for k,v in results.items():
        if k == 'results':
            print_results_summary(v, "\t")
        elif k != 'attachments':
            print("\t%s: %s" % (k, str(v)))
    print("Attachments:")
    results_diff = ""
    for idx, att in enumerate(results['attachments']):
        print("\t[%d] %s from %s for input '%s' : %s" % (idx, att['name'], att['output'], att['input'], att['mime-type'])) 
        if att['name'] == 'result-diff-csv':
            results_diff = att['data']

    print("Diff:")
    print(results_diff)
    print("Diff dataframe summary:")
    df = pd.read_csv(io.StringIO(results_diff), sep="|")
