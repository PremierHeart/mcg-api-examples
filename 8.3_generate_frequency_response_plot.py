#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import numpy as np
import pandas
import matplotlib.pyplot as plt

def plot_frequency_response_matrix(m, label, rownames):
    num_rows, num_cols = m.shape
    x = np.linspace(0,num_cols,num_cols)
    for a in range(0,num_rows):
        plt.plot(x, m[a:a+1].T, '-C' + str(a), label=rownames[a])
    plt.legend(loc='best')
    plt.xlabel("frequency")
    plt.ylabel("amplitude")
    plt.suptitle(label)
    plt.show()

def calc_frequency_response(dsp_m, rownames):
    # simplified calculation of frequency response: cps / aps
    m_ab = dsp_m['cps.(V5,II)']
    print("Frequency Response (V5):")
    m = dsp_m['aps.V5']
    # Note the out=/where= settings to prevent divide-by-zero
    m_out = np.divide(m_ab, m, out=np.zeros(m.shape), where=(m != 0))
    print(pandas.DataFrame(m_out).describe(include='all'))
    plot_frequency_response_matrix(m_out, "Frequency Response: V5", rownames)

    print("Frequency Response (II):")
    m = dsp_m['aps.II']
    m_out = np.divide(m_ab, m, out=np.zeros(m.shape), where=(m != 0))
    print(pandas.DataFrame(m_out).describe(include='all'))
    plot_frequency_response_matrix(m_out, "Frequency Response: II", rownames)

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
    dsp_row_names = []
    for att in get_transform_attachments(res):
        dsp_row_names.append(att['input'])
        for k in att['data'].keys():
            if k.startswith('json') or k == 'timestamp':
                continue
            if k not in dsp_data:
                dsp_data[k] = []
            dsp_data[k].append( np.array(att['data'][k]['data']) )

    # convert transform data to Numpy and Pandas for analysis
    dsp_m = { }
    for k, arr in dsp_data.items():
        # generate numpy matrices
        dsp_m[k] = np.matrix(arr)

    calc_frequency_response(dsp_m, dsp_row_names)
