#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import numpy as np
import pandas

def describe_dsp_dataframe(df, descr):
    # NOTE: This performs no actual analysis, but just describes the data
    print("(%s) %s of %s %s" % (descr['sym'], descr['name'], descr['source_type'], descr['source']))
    print("      %s domain: %s" % (descr['domain'], descr['label']))
    print(df.describe(include='all'))
    print()

def calc_frequency_response(dsp_m):
    # simplified calculation of frequency response: cps / aps
    m_ab = dsp_m['cps.(V5,II)']
    print("Frequency Response (V5):")
    m = dsp_m['aps.V5']
    # Note the out=/where= settings to prevent divide-by-zero
    m_out = np.divide(m_ab, m, out=np.zeros(m.shape), where=(m != 0))
    print(pandas.DataFrame(m_out).describe(include='all'))

    print("Frequency Response (II):")
    m = dsp_m['aps.II']
    m_out = np.divide(m_ab, m, out=np.zeros(m.shape), where=(m != 0))
    print(pandas.DataFrame(m_out).describe(include='all'))

def get_transform_attachments(res):
    for att in res['attachments']:
        if att['name'] == 'transform-sample':
            if att['mime-type'] == "application/json":
                att['data'] = json.loads(att['data'])
            yield att

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())
        
    # extract transform data from Results object into dict
    dsp_data = { }
    dsp_metadata = { }
    dsp_row_names = []
    for att in get_transform_attachments(res):
        dsp_row_names.append(att['input'])
        for k in att['data'].keys():
            if k.startswith('json') or k == 'timestamp':
                continue
            if k not in dsp_data:
                dsp_data[k] = []
            dsp_data[k].append( np.array(att['data'][k]['data']) )
            if k not in dsp_metadata:
                dsp_metadata[k] = { }
                dsp_metadata[k] = att['data'][k].copy()
                del dsp_metadata[k]['data']

    # convert transform data to Numpy and Pandas for analysis
    dsp_m = { }
    dsp_dataset = {}
    for k, arr in dsp_data.items():
        # generate numpy matrices
        dsp_m[k] = np.matrix(arr)
        # generate pandas dataset
        dsp_dataset[k] = pandas.DataFrame(data=dsp_m[k], index=dsp_row_names)

    # pretend-analysis: print descriptive statistics for each transform
    for k, df in dsp_dataset.items():
        describe_dsp_dataframe(df, dsp_metadata[k])

    # basic analysis: generate and print Frequency Response fo V5 and II
    calc_frequency_response(dsp_m)
    
