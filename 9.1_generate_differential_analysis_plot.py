#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import io
import sys
import json
import math
import pandas as pd
import matplotlib.pyplot as plt


default_dpi = 100
default_height = 768
default_width = 1024+1024

def plot_rows(ax, orig_df, diag_labels,legend=False):
    df = orig_df.iloc[:,3:]
    x_labels = []
    y_labels = []
    pos_x = [ ]
    pos_y = [ ]
    neg_x = [ ]
    neg_y = [ ]
    unstable_x = [ ]
    unstable_y = [ ]

    # diagnosis is Y axis
    for y, y_name in enumerate(df.columns):
        y_labels.append(y_name)
        # input is X axis
        for x_idx, row in df.iterrows():
            x_name = orig_df.inputs[x_idx]
            if isinstance(x_name, float):
                if math.isnan(x_name):
                    x_name = orig_df.groups[x_idx]
                else:
                    x_name = str(x_name) # actually an error
            if x_name not in x_labels:
                    x_labels.append(x_name)
            x = x_labels.index(x_name)

            # scatter plot point is either red X, Green +, or Blue -
            if row[y_name] == '+':
                pos_x.append(x)
                pos_y.append(y)
            elif row[y_name] == '-':
                neg_x.append(x)
                neg_y.append(y)
            else: # df.loc(idx, y) == 'X'
                unstable_x.append(x)
                unstable_y.append(y)

    ax.scatter(pos_x, pos_y, c='green', marker='P', label='always positive')
    ax.scatter(neg_x, neg_y, c='red', marker='_', s=100, label='always negative')
    ax.scatter(unstable_x, unstable_y, c='grey', marker='x', label='unstable')
    ax.grid(True, zorder=5, linestyle='dotted')
    if legend:
        ax.legend(loc='upper center', fontsize=6)

    ax.yaxis.set_ticks(list(range(len(y_labels))))
    if diag_labels:
        ax.set_yticklabels(y_labels, fontsize=8)  
    else:
        ax.set_yticklabels([])  

    ax.xaxis.set_ticks(list(range(len(x_labels))))
    ax.set_xticklabels(x_labels, rotation=315, ha='left', fontsize=6)  

def plot_differential(df,width=default_width, height=default_height, dpi=default_dpi):
    # NOTE: first five rows are comparison of both groups

    fig = plt.figure(figsize=[width/dpi, height/dpi], dpi=dpi)
    axes = fig.subplots(1, 4, width_ratios=[1, 3, 3, 3])

    # should be only two rows
    rows = df.loc[ df['operation'] == 'I']
    print(rows['operation'])
    ax = axes[0]
    ax.title.set_text("Identity operation")
    plot_rows(ax, rows, True, True)

    rows = df.loc[ df.operation.str.match(r"^A[0-9]*\^B[0-9]*")]
    print(rows['operation'])
    ax = axes[1]
    ax.title.set_text("Intersection (items in both B and A)")
    plot_rows(ax, rows, False)

    rows = df.loc[ df.operation.str.match(r"^A[0-9]*\-B[0-9]*")]
    print(rows['operation'])
    ax = axes[2]
    ax.title.set_text("Difference (items in A not in B)" )
    plot_rows(ax, rows, False)

    rows = df.loc[ df.operation.str.match(r"^B[0-9]*\-A[0-9]*")]
    print(rows['operation'])
    ax = axes[3]
    ax.title.set_text("Difference (items in B not in A)" )
    plot_rows(ax, rows, True)
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()

    fig.suptitle('MCG Diagnosis : Differential Analysis')
    fig.tight_layout()
    plt.show()
    plt.close()

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
        print("DIAGNOSIS MATRIX:")
        df = pd.DataFrame(summary['diagnosis-matrix'])

    print("Attachments:")
    results_diff = ""
    for idx, att in enumerate(res['attachments']):
        print("\t[%d] %s from %s for input '%s' : %s" % (idx, att['name'], att['output'], att['input'], att['mime-type']))
        if att['name'] == 'result-diff-csv':
            results_diff = att['data']

    print("Diff:")
    print(results_diff)
    print("Diff dataframe summary:")
    df = pd.read_csv(io.StringIO(results_diff), sep="|")
    plot_differential(df)
        
