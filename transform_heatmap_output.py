#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import json
import math
import sys
import numpy as np
import matplotlib.pyplot as plt                                                 

# transform applied to data before plotting, e.g. log()
log_and_round = lambda x: 0 if x == 0 else round(math.log(x))
xform_y_scale = {
        'aps': log_and_round,
        'amp': log_and_round,
        'cps': log_and_round,
}

default_dpi = 100
default_height = 768
default_width = 1024

def plot_heatmap(op_data, name, group, op, metadata, cmap="jet", width=default_width, height=default_height, dpi=default_dpi):
    op_sym = op.split('.')[0] # strip out source, if need be
    fig = plt.figure(figsize=[width/dpi, height/dpi], dpi=dpi)
    fig.suptitle(metadata['label'])
    ax = fig.gca()
    scale_fn = xform_y_scale[op] if op in xform_y_scale else None

    if scale_fn: op_data = [ list(map(scale_fn, row)) for row in op_data ]
    min_y = min( [ min(row) for row in op_data ] )
    max_y = max( [ max(row) for row in op_data ] )
    delta = float(max_y - min_y)
    if delta == 0:
        delta = 1
    rows = [ [(float(y-min_y) / delta) for y in row] for row in op_data ]

    im = ax.imshow(rows, cmap=cmap, interpolation='nearest',
                   aspect='auto', extent=(0,len(rows[0]), 0, len(rows)))
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    cb = fig.colorbar(im)
    # FIXME: Ticks should probably contain actual values
    # For now, just set to positive/negative
    cb.set_ticks([0.0, 1.0])
    cb.set_ticklabels(['-', '+'])

    # ----------------------------------------------------------------------
    # Display/Save plot
    print("Plotting %s. Press Ctrl-w to close." % op)
    plt.show()
    plt.close()


# ----------------------------------------------------------------------
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
    dsp_row_name = []
    dsp_row_group = []
    for att in get_transform_attachments(res):
        dsp_row_name.append(att['input'])
        dsp_row_group.append(att['group'])
        for k in att['data'].keys():
            if k.startswith('json') or k == 'timestamp':
                continue
            if k not in dsp_data:
                dsp_data[k] = []
            dsp_data[k].append( att['data'][k]['data'] )
            if k not in dsp_metadata:
                dsp_metadata[k] = { }
                dsp_metadata[k] = att['data'][k].copy()
                del dsp_metadata[k]['data']

    for op, op_data in dsp_data.items():
        op_metadata = dsp_metadata[op]
        plot_heatmap(dsp_data[op], dsp_row_name, dsp_row_group, op, op_metadata)

