#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import base64
from datetime import datetime
import numpy as np
import pandas

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

def parse_feature_attachment(att):
    data = retrieve_attachment(att)
    ts = datetime.utcfromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

    xforms = list(set(data.keys()) - set(['timestamp', 'json-schema', 'json_class']))
    xforms.sort()
    feature_values = { 'timestamp': ts }
    for xform_sym in xforms:
        xform = data[xform_sym] 
        for feat_sym in xform['features'].keys():
            key = xform_sym +'.' + feat_sym
            feature_values[key] = xform['features'][feat_sym]['value']
    return feature_values

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    col_names = None
    rows = []
    row_names = []
    for idx, att in enumerate(res['attachments']):
        if att['output'] == 'feature-json' and att['name'] == 'feature-sample':
            row_names.append(att['input'])
            feat_h = parse_feature_attachment(att)
            if not col_names:
                col_names = list(feat_h.keys())
                col_names.sort()
            row = []
            for sym in col_names:
                row.append( feat_h[sym] )
            rows.append(row)
    # generate pandas dataset
    feat_dataset = pandas.DataFrame(data=np.matrix(rows), index=row_names, columns=col_names)
    print(feat_dataset.describe(include='all'))
