#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import base64
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

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

def parse_feature_attachment(att):
    data = retrieve_attachment(att)
    ts = datetime.utcfromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

    xforms = list(set(data.keys()) - set(['timestamp', 'json-schema', 'json_class']))
    xforms.sort()
    feature_values = { }
    for xform_sym in xforms:
        xform = data[xform_sym] 
        for feat_sym in xform['features'].keys():
            key = xform_sym +'.' + feat_sym
            feature_values[key] = xform['features'][feat_sym]['value']
    return feature_values

# colormap: grey if negative, green -> yellow -> red -> black if positive
feat_cmap = sar_cmap = LinearSegmentedColormap('mcg_sar_cmap',
    {'red': ((0.0, 0.8, 0.8),
        (0.15, 0.0, 0.0),
        (0.3, 0.0, 0.0),
        (0.6, 0.7, 0.7),
        (1.0, 1.0, 0.0)),
    'green': ((0.0, 0.8, 0.8),
        (0.15, 0.5, 0.9),
        (0.3, 1.0, 1.0),
        (0.6, 0.8, 0.8),
        (1.0, 0.0, 0.0)),
    'blue': ((0.0, 0.8, 0.8),
        (0.15, 0.0, 0.0),
        (0.3, 0.0, 0.0),
        (0.6, 0.0, 0.0),
        (1.0, 0.0, 0.0))}, 256)
   
def normalize_feature_value(val):
     if val < 0.0:
         val = 0.0
     elif val > 3.0:
         val = 3.0
     return val / 3.0

def plot_feature_matrix(m, y_labels, x_labels):
    normalize = np.vectorize(normalize_feature_value)
    m = normalize(m)
    fig = plt.figure()
    num_rows, num_cols = m.shape
    ax = fig.gca()
    im = ax.imshow(m, cmap=feat_cmap, aspect='auto',
                   extent=(0,num_cols, 0, num_rows),                       
                   origin='lower', interpolation='none')
    ax.set_xlim(0,len(x_labels))
    ax.set_ylim(0,len(y_labels))
    ax.set_xticks(list(range(len(x_labels))))
    ax.set_xticklabels(x_labels, rotation=270, fontsize=6)
    ax.set_yticks(list(range(1, len(y_labels)+1)))
    ax.set_yticklabels(y_labels, fontsize=8)
    # add grid lines for each sample
    ax.grid(which='major', axis='y', linestyle='-', color='black')
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    col_names = None
    rows = []
    row_names = []
    for idx, att in enumerate(res['attachments']):
        if att['output'] == 'feature-json' and att['name'] == 'feature-sample':
            row_names.append(att['input'])
            feat_h = parse_feature_attachment(att)
            if not col_names:
                col_names = list(feat_h.keys())
                col_names.sort()
            row = []
            for sym in col_names:
                row.append( feat_h[sym] )
            rows.append(row)
    plot_feature_matrix(np.matrix(rows, dtype=float), row_names, col_names)
