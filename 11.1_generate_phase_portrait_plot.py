#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def normalize(data):
    x_min = float(min(data))
    delta = float(max(data)) - x_min
    if delta == 0:
        delta = 0.00001
    return [ ((float(x) - x_min) / delta) for x in data ]

def plot_phase_portrait_column(axes, col, name, pp):
    x = pp['x']
    y = pp['y']
    X, Y = np.meshgrid(x, y, sparse=True)
    u = np.cos(X)
    v = np.sin(Y)

    # v5 plots
    ax = axes[0][col]
    ax.title.set_text(name + " Phase Portrait : quiver" )
    ax.quiver(X,Y, u, v, scale=25, pivot='mid')
    ax.set_xticks([])
    ax.set_yticks([])

    ax = axes[1][col]
    ax.title.set_text(name + " Phase Portrait : scatter" )
    ax.scatter(x, y, s=1, marker='_')
    ax.set_xlim([min(x), max(x)])
    ax.set_ylim([min(y), max(y)])
    ax.set_xticks([])
    ax.set_yticks([])

    ax = axes[2][col]
    ax.title.set_text(name + " Phase Portrait : line" )
    ax.plot(x, y, linewidth=0.05)
    ax.set_xlim([min(x), max(x)])
    ax.set_ylim([min(y), max(y)])
    ax.set_xticks([])
    ax.set_yticks([])

def plot_phase_portrait(ppv5, ppii):
    fig, axes = plt.subplots(3, 2)

    plot_phase_portrait_column(axes, 0, 'V5', ppv5)
    plot_phase_portrait_column(axes, 1, 'II', ppii)

    plt.show()        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    if (res['object-type'] != 'analysis-result') or ('results' not in res):
        print("Invalid JSON AnalysisResults object!")
        sys.exit()

    summary = res['results']
    if 'phase-portrait' not in summary:
        print("AnalysisResults Summary is missing 'phase-portrait' section")
        sys.exit()

    # FIXME: create dataframe
    # to plot each lead:
    #for lead, pp in summary['phase-portrait'].items():

    ppv5 = summary['phase-portrait']['V5']
    ppii = summary['phase-portrait']['II']
    plot_phase_portrait(ppv5, ppii)

