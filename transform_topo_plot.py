#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import json
import math
import sys
import numpy as np
import matplotlib.pyplot as plt                                                 
from matplotlib import colormaps as cm
import matplotlib.collections as coll

# transform applied to data before plotting, e.g. log()
log_and_round = lambda x: 0 if x == 0 else round(math.log(x))
xform_y_scale = {
        'aps': log_and_round,
        'amp': log_and_round,
        'cps': log_and_round,
}

#  min, max, length
xform_range = {
  'amp' : [0,10, 100],
  'amp.V5' : [0,10, 100],
  'amp.II' : [0,10, 100],
  'aps' : [0,8, 128],
  'aps.V5' : [0,8, 128],
  'aps.II' : [0,8, 128],
  'ccr' : [0,50, 512],
  'coh' : [0,300, 128],
  'imr' : [-250,250, 256],
  'psa' : [-250,250, 128],
  'xar' : [0,250, 128],
  'cps' : [0,12, 128]
}

xform_transparency = {
  'amp' :  0.75,
  'aps' :  0.75,
  'ccr' :  0.75,
  'coh' :  0.75,
  'imr' :  0.85,
  'psa' :  0.50,
  'xar' :  0.75,
  'cps' :  0.75
}

xform_x_ticks = {
  'amp' : [0, 25, 50, 75, 100],
  'aps' : [0, 16, 32, 48, 64, 80, 96, 112, 128],
  'ccr' : [0, 128, 256, 384, 512],
  'coh' : [0, 32, 64, 96, 128],
  'imr' : [0, 64, 128, 192, 256],
  'psa' : [0, 32, 64, 96, 128],
  'xar' : [0, 32, 64, 96, 128],
  'cps' : [0, 32, 64, 96, 128]
}

xform_y_ticks = {
  'amp' : [0, 5, 10],
  'aps' : [0, 5, 8],
  'ccr' : [0, 25, 50],
  'coh' :[0, 100, 200, 300],
  'imr' : [-250, 0, 250],
  'psa' : [-250, 0, 250],
  'xar' : [0, 50, 100, 150, 200, 250],
  'cps' : [0, 8, 12]
}


# ----------------------------------------------------------------------
# BUILT-IN TRANSFORM TITLES

xform_x_title = {
  'amp': 'Amplitude in mV',
  'amp.V5': 'Amplitude in mV',
  'amp.II': 'Amplitude in mV',
  'aps': 'Frequency in Hz',
  'ccr': 'Time in ms',
  'coh': 'Frequency in Hz',
  'imr': 'Latency',
  'psa': 'Frequency in Hz',
  'xar': 'Frequency in Hz',
  'cps': 'Frequency in Hz'
}

xform_y_title = {
  'amp': 'log(Count)',
  'aps': 'log(Power in Watts)',
  'ccr': 'Amplitude in mV',
  'coh': 'Square of Amplitude Ratio',
  'imr': 'Amplitude in mV',
  'psa': 'Phase Shift in Degrees',
  'xar': 'Amplitude Ratio of CPS:APS',
  'cps': 'Power in Watts'
}

# Available colormaps - note only 6 groups are supported
color_maps = [ 
  'Greens', 'Oranges', 'Blues', 'Reds', 'Purples', 'Greys' 
]

default_dpi = 100
default_height = 768
default_width = 1024+1024 # 2 plots


# Return start and end coordinates for each band of color in a group. This is
# used to apply the polygon colors to the 3-D countour plot.
def group_color_coords(plot_data):
    colors = []
    starts = []
    ends = []

    curr_col = None
    for idx, col in enumerate(plot_data['row_colors']):
        if col != curr_col:
            colors.append(col)
            starts.append(idx)
            if idx > 0: ends.append(idx)
        curr_col = col
    ends.append(len(plot_data['row_colors']) - 1)

    rects = [ ]
    for idx, c in enumerate(colors):
        rects.append( {'color': c, 'start': starts[idx], 'end': ends[idx] } )
    return rects


# Generate a Hash with plot data calculated from padding and DSP Data. 
# The Hash has the following keys:
#  :rows
#  :row_colors
#  :group_ticks
#  :vertices : Used by 3-D polygon plot
#  :x : Used by contour plot and 3-D surface plot
#  :y : Used by contour plot and 3-D surface plot
#  :z : Used by contour plot and 3-D surface plot
# Note that padding is used on the edges of the plot to ensure that the data
# appears as peaks offset from zero, rather than as a surface.
def generate_plot_data(data, group, op, baseline=0):
    def append_data(plot_data, data, curr_y, color):
      # polygon plot data
      y_data = [0] + data + [0] # spacing
      plot_data['vertices'].append( list(zip(range(0, len(y_data)), y_data)) )
      plot_data['rows'].append(curr_y)
      plot_data['row_colors'].append(color)

      # contour plot data
      if curr_y >= len(plot_data['z']): plot_data['z'].append([])
      plot_data['z'][curr_y].append(0)  # spacing
      plot_data['z'][curr_y] += data
      plot_data['z'][curr_y].append(0)  # spacing

    greys = cm.get_cmap('Greys') # padding is always grey
    def append_padding(plot_data, pad_value, data_len, curr_y):
        append_data(plot_data, [pad_value] * data_len, curr_y, greys(50))

    # generate dict of data groups
    h = {}
    for idx, arr in enumerate(data):
        grp = group[idx] if idx < len(group) else ""
        if grp not in h: h[grp] = [] 
        h[grp].append(arr)

    plot_data = { 'vertices': [], 'rows': [], 'row_colors': [],
                  'x': [], 'y': [], 'z': [], 'group_ticks': {} }
    
    curr_y = 0
    curr_color = 0
    pad = baseline
    scale_fn = xform_y_scale[op] if op in xform_y_scale else None

    data_len = len(data[0])
    for grp, items in h.items():
        append_padding(plot_data, pad, data_len, curr_y) # pad befre each group

        # Get colormap of this group
        curr_y += 1
        if curr_color >= len(color_maps):
            curr_color = 0
        cmap = cm.get_cmap(color_maps[curr_color])

        plot_data['group_ticks'][grp] = curr_y # save group y-loc and name

        # add tests
        color_value = 0.25 # don't start at white!
        color_inc = (1.0 - color_value) / len(items)
        for samp in items:
            if scale_fn: samp = list(map(scale_fn, samp))
            color_value += color_inc
            append_data(plot_data, samp, curr_y, cmap(color_value))
            curr_y += 1

        curr_color += 1 # change color for next group

    append_padding(plot_data, pad, data_len, curr_y) # pad after last group
    curr_y += 1

    plot_data['x'] = list(range(0, data_len+2)) # +2 for zero paddings
    plot_data['y'] = list(range(0, curr_y))

    return plot_data

# ----------------------------------------------------------------------
# data is a dict of op-name to op-data (array)
# name is an array providing the name of each row (sample)
# group is an array providing name of group for each sample
#
# width, height, dpi, transparency
# specify group order?
def plot_topo(data, name, group, op, metadata, width=default_width, height=default_height, dpi=default_dpi):
    op_sym = op.split('.')[0] # strip out source, if need be
    plot_data = generate_plot_data(data, group, op_sym)

    fig = plt.figure(figsize=[width/dpi, height/dpi], dpi=dpi)
    fig.suptitle(metadata['label'])

    # -----------------------------------------------------------------------
    # 3-D Polygon Plot
    # 121 is 1 row x 2 col, subplot #1 (incrementing by row)
    ax = fig.add_subplot(121, projection= '3d')
    verts = np.array(plot_data['vertices'])
    rows = np.array(plot_data['rows'])

    # per-group color gradient, each in-group sample having its own color
    fc = plot_data['row_colors']
    poly = coll.PolyCollection(verts, facecolors=fc)
    trans = xform_transparency.get(op_sym, 0.8)
    poly.set_alpha(trans)
    ax.add_collection3d(poly, zs=rows, zdir='y')

    # X-Axis (DSP X-axis)
    x_max = max(plot_data['x']) 
    ax.set_xlim3d(0, x_max)
    # BUG: X labels not being set in DSP
    #ax.set_xlabel(metadata['x_label'])
    ax.set_xlabel(xform_x_title.get(op_sym,'X'))
    if op_sym in xform_x_ticks: ax.set_xticks(xform_x_ticks[op_sym])

    # Z-axis (DSP Y-axis)
    y_max = max(map(lambda x: max(x), plot_data['z']))
    ax.set_zlim3d((0, y_max))
    # BUG: Y labels not being set in DSP
    #ax.set_zlabel(metadata['y_label'])
    ax.set_zlabel(xform_y_title.get(op_sym, 'Y'))
    if op_sym in xform_y_ticks: ax.set_zticks(xform_y_ticks[op_sym]) 

    # Y-axis (sample/group)
    group_labels = list(plot_data['group_ticks'].keys())
    ax.set_ylim3d(0, len(plot_data['rows']))
    ax.yaxis.set_ticks(list(plot_data['group_ticks'].values()))
    ax.yaxis.set_ticklabels(group_labels, rotation=-15, verticalalignment='baseline', horizontalalignment='left')

    # ----------------------------------------------------------------------
    # CONTOUR
    ax = fig.add_subplot(122)
    grid_x = np.array(plot_data['x'])
    grid_y = np.array(plot_data['y'])
    # Z data must be 2-D
    grid_z = np.array([ np.array(arr) for arr in plot_data['z'] ])
    col_coord = group_color_coords(plot_data)
    for h in col_coord:
        # NOTE: trans calculated above
        ax.axhspan(h['start'], h['end'], facecolor=h['color'], alpha=trans)
    
    ax.contour(grid_x, grid_y, grid_z, 15, linewidths=0.5, colors='k')
    
    # X-Axis (DSP X-axis)
    ax.set_xlim(0, x_max)
    ax.set_xlabel(xform_x_title[op] if op in xform_x_title else 'X')
    if op in xform_x_ticks: ax.set_xticks(xform_x_ticks[op])

    # Y-axis (sample/group)
    ax.set_ylim(0, len(plot_data['rows']))
    ax.yaxis.set_ticks(list(plot_data['group_ticks'].values()))
    ax.yaxis.set_ticklabels(group_labels)

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
        plot_topo(dsp_data[op], dsp_row_name, dsp_row_group, op, op_metadata)

