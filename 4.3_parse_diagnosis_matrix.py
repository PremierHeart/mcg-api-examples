#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import json
import requests
import os
import random
import sys
from datetime import datetime

def print_diagnosis_matrix(res, delim="\t"):
    if len(res) < 1:
        return
    rows = [ [samp] for samp in res['id'] ]
    col_names = ['Condition']
    for diag, scores in res.items():
        if diag != 'id':
            col_names.append(diag)
            for idx, score in enumerate(scores):
                rows[idx].append(str(score))
    print(delim.join(col_names))
    for row in rows:
        print(delim.join(row))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Missing analysis_results.json argument!\n")         
        sys.exit(-1)  
        
    with open(sys.argv[1], 'r') as f:         
        res = json.loads( f.read() ) 

        if res['object-type'] != 'analysis-result':
            print("Unexpected return value from API server:")
            for k,v in res.items():
                print("\t%s: %s" % (k, v))
            sys.exit()

        if 'diagnosis-matrix' in res['results']:
            print_diagnosis_matrix(res['results']['diagnosis-matrix'], "|")
        else:
            print("Diagnosis-matrix option was not provided to analysis!")
