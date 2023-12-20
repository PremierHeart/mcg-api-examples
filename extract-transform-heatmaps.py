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

    for att in res['attachments']:
        if not att['name'].startswith('transform-heatmap'):
            continue
        if not att['mime-type'] == 'image/svg+xml':
            continue

        data = att['data']
        if att['encoding'] == 'base64':
            data = base64.b64decode(data)

        fname = 'images/' + att['name'] + '.svg'
        print("Writing " + fname + '...')
        with open(fname, 'wb') as f: 
            f.write(data)
            
    print('Done.')
