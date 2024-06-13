#!/usr/bin/env python
# (c) Copyright 2024 Premier Heart, LLC

import json
import requests
import os
import random
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
          "report-json": { 
              "in-place-json": True 
          }
      }, 
      "input": inputs,
    }

def input_for_ecg_json(json_str, ident=None, age=40, gender='M'):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rec = {
      "type": "ecg",
      "format": "json",
      "timestamp": ts,
      "age": age,
      "gender": gender,
      "data": json.loads(json_str)
    }
    if ident:
        rec["name"] = ident
    return rec

def decode_response(resp):
    if resp.status_code != 200:
        return {
                "object-type": "http-error",
                "timestamp": str(datetime.now),
                "message": "Unknown error: HTTP %d" % resp.status_code
        }
    return json.loads(resp.text)

def get_report_data(res):
    summary = res['results']

    diags = { 'Tracing Quality': {} }
    for ident, score in summary['tracing-quality'].items():
        diags['Tracing Quality'][ident] = str(score)

    final = { 'MCG Category': summary['category'] }
    for name, val in summary['positive'].items():
        final[name] = val
    for name, val in summary['negative'].items():
        final[name] = False

    dsp = {}
    for att in res['attachments']:
        if att['name'] == 'report':
            for rec in att['data']:
                ident = rec['input']
                # get diagnoses
                for name, h in rec['results'].items():
                    if name == 'tracing-quality':
                        continue
                    if name not in diags:
                        diags[name] = { }
                    diags[name][ident] = str(h['value'])

                for name, arr in rec['transforms'].items():
                    if name not in dsp:
                        dsp[name] = { }
                    dsp[name][ident] = arr
    return { 'final': final, 'results': diags, 'transforms': dsp }

def display_report_data(rpt):
    print("MCG Analysis Results")
    print("--------------------")
    for name, val in rpt['final'].items():
        score = "-"
        if val != False:
            score = "+ (" + str(val) + ")"
        print("    %s: %s" % (name, score))

    print("Per-Sample Results")
    print("------------------")
    for name, h in rpt['results'].items():
        print("    %s: %s" % (name, ", ".join(h.values())))

    print("Per-Sample Plots")
    print("----------------")
    for name, h in rpt['transforms'].items():
        print("    PLOT %s FOR %s" % (name, ", ".join(h.keys())))

if __name__ == '__main__':
    url = "https://api.premierheart.com/api/v1/analyze"
    if len(sys.argv) > 1:
        url = sys.argv[1]

    inputs = [ ]
    for x in range(3):
        fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', ("ecg_%d.json" % (x+1)))
        with open(fname, 'r') as f:
            ident = os.path.basename(fname)
            inputs.append(input_for_ecg_json(f.read(), ident))
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

    rpt =  get_report_data(results)
    display_report_data(rpt)
