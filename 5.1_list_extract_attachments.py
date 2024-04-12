#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import base64

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

        # retrieve data for attachment
        data = att['data']
        if att['encoding'] == 'base64':
            # att['data'] is a base64-encoded object such as a binary file
            data = base64.b64decode(data)
        if att['mime-type'] == 'application/json':
            # att['data'] is a string containing JSON
            data = json.loads(data)
        # at this point, the program can display or operate on 'data'

        # write attachment to file on disk
        output_data = att['data']
        if att['mime-type'] == 'application/x-java-object':
            # This is an inline JSON object and must be serialized
            output_data = json.dumps(att['data'])
        # NOTE: This does not determine filename extension
        fname = att['name'] + '.dat'
        print("Writing " + fname + '...')
        with open(fname, 'w') as f: 
            f.write(output_data)
