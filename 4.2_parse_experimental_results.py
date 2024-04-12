#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import json
import os
import sys

def print_score_range(res, indent):
    print(indent + "Condition score range:")
    for diag, stats in res['range'].items():
        print(indent + indent + "%s : %s" % (diag, str(stats)))

def print_representative_test(res, indent):
    print(indent + "Results from using input %s as a representative sample:" % res['sample'])
    for diag, score in res['representative'].items():
        if isinstance(score, str):
            print(indent + indent + "%s : %s" % (diag, score))
        else:
            print(indent + indent + "%s : %0.1f" % (diag, score))

def print_aggregate_analysis(res, indent):
    print(indent + "Results from experimental aggregate analysis:")
    for diag, score in res['aggregate'].items():
        if isinstance(score, str):
            print(indent + indent + "%s : %s" % (diag, score))
        else:
            print(indent + indent + "%s : %0.1f" % (diag, score))

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

        print("Attachments: %d" % (len(res['attachments'])))

        print("Results Summary:")
        print_score_range(res['results'], "\t")
        print_representative_test(res['results'], "\t")
        print_aggregate_analysis(res['results'], "\t")
