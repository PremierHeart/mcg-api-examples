#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import base64
from datetime import datetime

def retrieve_attachment(att):
    # retrieve data for attachment
    data = att['data']
    if att['encoding'] == 'base64':
        # att['data'] is a base64-encoded object such as a binary file
        data = base64.b64decode(data)
    if att['mime-type'] == 'application/json':
        # att['data'] is a string containing JSON
        data = json.loads(data)
    # otherwise, att['data'] is inline-json and is already unpacked
    return data

def print_result_attachment(att):
    data = retrieve_attachment(att)
    ts = datetime.utcfromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    print("\"%s\" %s" % (att['input'], ts))  
    algos = list(set(data.keys()) - set(['timestamp', 'json-schema', 'json_class']))
    algos.sort()
    for algo_sym in algos:
        algo = data[algo_sym]
        print("\t[%s] %s" % (algo['sym'], algo['name']))
        diags = list(algo['diagnoses'].keys())
        diags.sort()
        for diag_sym in diags:
            diag = algo['diagnoses'][diag_sym]
            pos = '+' if diag['positive'] else '-'
            print("\t\t[%s] %s (%s) : %s" % (diag_sym, diag['name'], pos, str(diag['value'])))
            for ref in diag['refs']:
                print("\t\t\t[%s] %s.%s \"%s\" (%0.1f" % (ref['type'], ref['component'],ref['source'], ref['item'], ref['weight']))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    for idx, att in enumerate(res['attachments']):
        if att['output'] == 'result-json' and att['name'] == 'result-sample':
            print_result_attachment(att)
