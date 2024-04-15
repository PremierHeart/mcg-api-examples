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

def print_feature_attachment(att):
    data = retrieve_attachment(att)
    ts = datetime.utcfromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

    print("\"%s\" %s" % (att['input'], ts))  
    xforms = list(set(data.keys()) - set(['timestamp', 'json-schema', 'json_class']))
    xforms.sort()
    for xform_sym in xforms:
        xform = data[xform_sym] 
        print("\t[%s] %s" % (xform_sym, xform['name']))
        feats = list(xform['features'].keys())
        feats.sort()
        for feat_sym in feats:
            feat = xform['features'][feat_sym]
            pos = '+' if feat['positive'] else '-'
            print("\t\t[%s] %s (%s) : %0.1f" % (feat_sym, feat['name'], pos, feat['value']))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    for idx, att in enumerate(res['attachments']):
        if att['output'] == 'feature-json' and att['name'] == 'feature-sample':
            print_feature_attachment(att)
