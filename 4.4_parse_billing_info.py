#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import json
import os
import sys

def print_billing_info(res):
        billing_info = [ ]
        if 'invoice-id' in res:
            billing_info.append("Invoice ID:" +  str(res['invoice-id']))
        if 'billing-info' in res:
            for k, v in res['billing-info'].items():
                billing_info.append("%s: %s" % (k,str(v)))
        if len(billing_info) > 0:
            print("Billing Info:")
            for line in billing_info:
                print("\t" + line)

        if 'comment' in res:
            print("Comment: " + res['comment'])


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

        print_billing_info(res['results'])
