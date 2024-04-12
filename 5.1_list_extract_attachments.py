#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import base64

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

def write_attachment_to_disk(att):
    # write attachment to file on disk
    output_data = retrieve_attachment(att)
    mode = "wb"
    if (att['mime-type'] == 'application/x-java-object') or \
       (att['mime-type'] == 'application/json'):
        # This is an inline JSON object and must be serialized
        output_data = json.dumps(output_data)
        mode = "w"

    # NOTE: This does not determine filename extension
    fname = + att['name'] + '.dat'
    print("Writing " + fname + '...')
    with open(fname, mode) as f: 
        f.write(output_data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    for idx, att in enumerate(res['attachments']):
        # list attachment
        print("[%d] %s.%s : %s %s (%s;%s)" % (idx,
            att['output'], att['name'],
            att['group'], att['input'],
            att['mime-type'], att['encoding']))

        data = retrieve_attachment(att)
        raw_cls = att['data'].__class__.__name__
        xlat_cls =  data.__class__.__name__
        print("     Data of class %s -> class %s" % (raw_cls, xlat_cls))

        write_attachment_to_disk(att)
