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

def parse_transform_attachment(att):
    data = retrieve_attachment(att)
    ts = datetime.utcfromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    print("\"%s\" %s" % (att['input'], ts))
    xforms = list(set(data.keys()) - set(['timestamp', 'json-schema', 'json_class']))
    xforms.sort()
    for sym in xforms:
        xform = data[sym]
        print("\t[%s] %s of %s %s" % (sym, xform['name'], xform['source_type'], xform['source']))
        print("\t\tDomain: %s" % xform['domain'])
        print("\t\tPlot Title: %s" % xform['label'])
        print("\t\t     X-axis: %s" % xform['x_label'])
        print("\t\t     Y-axis: %s" % xform['y_label'])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    for idx, att in enumerate(res['attachments']):
        if att['output'] == 'transform-json' and att['name'] == 'transform-sample':
            parse_transform_attachment(att)
