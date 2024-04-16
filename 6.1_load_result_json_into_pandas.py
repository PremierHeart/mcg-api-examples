#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import numpy as np
import pandas as pd

def generate_diagnosis_algorithm_dataset(res):
    algos = { }
    idents = [ ]
    descr = { }
    for att in get_diagnosis_attachments(res):
        idents.append(att['input'])
        for k in att['data'].keys():
            if k.startswith('json') or k == 'timestamp':
                continue
            algo = att['data'][k]
            if k not in algos:
                algos[k] = { }
            if k not in descr:
                descr[k] = algo['name']
            for sym, diag in algo['diagnoses'].items():
                if sym not in algos[k]:
                    algos[k][sym] = [ ]
                algos[k][sym].append(diag['value']['data'])

    ds = { }
    for sym, diags in algos.items():
        df = pd.DataFrame(diags)
        df['input'] = idents
        ds[descr[sym]] = df
    return ds

def diag_value_to_str(val):
    if val['type'] == 'I':
        return "%d" % val['data']
    elif val['type'] == 'f':
        return "%0.2f" % val['data']
    elif val['type'] == 'a':
        return val['data']
    else:
        return str(val['data'])

def get_diagnosis_attachments(res):
    for att in res['attachments']:
        if att['name'] == 'result-sample':
            # replace JSON-encoded string with decoded object
            if att['mime-type'] == "application/json":
                att['mime-type'] = "application/x-java-object"
                att['data'] = json.loads(att['data'])
            yield att

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    if (res['object-type'] != 'analysis-result') or ('results' not in res):
        print("Invalid JSON AnalysisResults object!")
        sys.exit()

    summary = res['results']
    if 'diagnosis-matrix' in summary:
        print("---DIAGNOSIS MATRIX---")
        df = pd.DataFrame(summary['diagnosis-matrix'])
        pd.options.display.max_columns = None
        print(df.describe(include=np.number))

    # print results-json contents for each input:
    for att in get_diagnosis_attachments(res):
        for k in att['data'].keys():
            if k.startswith('json') or k == 'timestamp':
                continue
            algo = att['data'][k]
            for sym, diag in algo['diagnoses'].items():
                pos = "-"
                if diag['positive']:
                    pos = '+'

    # extract transform data from Results object into dict
    algo_ds = generate_diagnosis_algorithm_dataset(res)
    for name, df in algo_ds.items():
        print("---%s---" % name.upper())
        print(df.describe(include=np.number))
        #print(df.select_dtypes(include='number'))
