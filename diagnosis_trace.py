#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import json
import requests
import os
import random
import base64
import sys
from datetime import datetime

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
        "type": "mcg-aggregate",
        "options": {
          "diagnosis-matrix": True
        }
      },
      "output": {
        "result-json": {
            'in-place-json': True
        },
        "result-explain-json": {
            'in-place-json': True
        },
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

    print(indent + "Diagnosis generated by %s using input %s as a representative sample" % (res['source'], res['sample']))
    print(indent + "MCG Category: %s" % res['category'])

    print_basic_results(res, indent)

    print_tracing_quality(res, indent)

def print_basic_results(res, indent):
    print(indent + "Conditions detected (positives):")
    for diag, score in res['positive'].items():
        print(indent + indent + "%s : %0.1f" % (diag, score))
        
    print(indent + "Conditions not detected (negatives):")
    for diag, score in res['negative'].items():
        print(indent + indent + "%s : %0.1f" % (diag, score))

def print_tracing_quality(res, indent):
    print(indent + "Tracing Quality:")
    for samp, tq in res['tracing-quality'].items():
        print(indent + indent + "%s : %d" % (samp, tq))

if __name__ == '__main__':
    url = "https://api.premierheart.com/api/v1/analyze"
    if len(sys.argv) > 1:
        url = sys.argv[1]

    inputs = [ ]
    for x in range(3):
        fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', ("ecg_%d.json" % (x+1)))
        with open(fname, 'r') as f:
            h_input = input_for_ecg_json(f.read())
            h_input['name'] = os.path.splitext(os.path.basename(fname))[0]
            h_input['group'] = 'screen'
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
    with open("data/analysis-results.multiple-outputs.example.json", 'w') as f:
        f.write(json.dumps(results))

    print("Results Summary:")
    for k,v in results.items():
        if k == 'results':
            print_results_summary(v, "\t")
        elif k != 'attachments':
            print("\t%s: %s" % (k, str(v)))
    print("Attachments:")
    diag_trace = { }
    for idx, att in enumerate(results['attachments']):
        # The contents of the attachment are in att['data'] 
        # but may be base64-encoded.
        mem = 'unknown data object'
        if att['encoding'] == 'base64':
            mem = "base64-encoded %d-byte file" % len(base64.b64decode(att['data']))
        elif att['mime-type'] == 'application/x-java-object':
            mem = "in-memory JSON object"

        print("\t[%d] %s from %s for input '%s' : %s (%s)" % (idx, att['name'], att['output'], att['input'], att['mime-type'], mem)) 

        if att['name'] == 'result-explain-sample':
            diag_trace[att['input']] = att['data']
    print(diag_trace)
    #{'ecg_1': {'IMPSTR': {'name': 'Impression (text)', 'backtrace': {'MCG Primary Analysis: Impression (text)'

    