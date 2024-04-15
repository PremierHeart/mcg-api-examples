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

def parse_transform_attachment(att):
    data = retrieve_attachment(att)
    ts = datetime.utcfromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    xforms = list(set(data.keys()) - set(['timestamp', 'json-schema', 'json_class']))
    xforms.sort()
    xform_keys = None
    h = { }
    for sym in xforms:
        xform = data[sym]
        if not xform_keys:
            xform_keys = list(xform.keys())
            xform_keys.remove("data")

        metadata = {}
        for key in xform_keys:
            metadata[key] = xform[key]
        metadata["timestamp"] = ts
        h[sym] = [metadata, xform["data"]]
    return h

def describe_dsp_dataframe(df, descr):
    print("(%s) %s of %s %s" % (descr['sym'], descr['name'], descr['source_type'], descr['source']))
    print("      %s domain: %s" % (descr['domain'], descr['label']))
    print(df.describe(include='all'))
    print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    dsp_data = { }
    dsp_metadata = { }
    dsp_row_names = []
    for idx, att in enumerate(res['attachments']):
        if att['output'] == 'transform-json' and att['name'] == 'transform-sample':
            dsp_row_names.append(att['input'])
            dsp_h = parse_transform_attachment(att)
            for sym, xform_data in dsp_h.items():
                metadata = xform_data[0]
                data = xform_data[1]
                if sym not in dsp_data:
                    dsp_data[sym] = []
                dsp_data[sym].append( np.array(data) )
                if sym not in dsp_metadata:
                    dsp_metadata[sym] = []
                    dsp_metadata[sym] = metadata

    dsp_dataset = {}
    for sym, data in dsp_data.items():
        # generate pandas dataset
        dsp_dataset[sym] = pandas.DataFrame(data=np.matrix(data), index=dsp_row_names)

    # print descriptive statistics for each transform
    for k, df in dsp_dataset.items():
        describe_dsp_dataframe(df, dsp_metadata[k])


