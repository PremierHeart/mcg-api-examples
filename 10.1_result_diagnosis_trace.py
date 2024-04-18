#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json

def print_trace_hash(h, indent, level):
    for label, trace in h.items():
        recurse = False
        if isinstance(trace, dict):
            val = ""
            recurse = True
        else:
            val = str(trace)
        print((indent*level) + label + ':' + val)
        if recurse:
            print_trace_hash(trace, indent, level+1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    if (res['object-type'] != 'analysis-result') or ('results' not in res):
        print("Invalid JSON AnalysisResults object!")
        sys.exit()

    for att in res['attachments']:
        if att['name'] == 'result-explain-sample':
            print("Diagnosis trace: " + att['input'])
            # replace JSON-encoded string with decoded object
            if att['mime-type'] == "application/json":
                att['mime-type'] = "application/x-java-object"
                data = json.loads(att['data'])
            else:
                data = att['data']
            for diag, trace in data.items():
                print("    [%s] %s:" % (diag, trace['name']))
                print_trace_hash(trace['backtrace'], "   ", 2)
    
