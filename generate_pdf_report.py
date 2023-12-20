#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import datetime as dt
from fpdf import FPDF # pip install fpdf2
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from PIL import Image


def create_pdf(res):
    doc = FPDF()
    return doc

SPECIAL_CONDITIONS = ["Impression", "Disease Severity", "Disease Severity Adjusted Score", "Ischemic Disease Severity", "Global Ischemia", "Local Ischemia", "Global Ischemia (borderline)", "Local Ischemia (borderline)"]
def impression_to_text(score):
    if score <= 1:
        return "Normal"
    elif score > 4:
        return "Abnormal"
    else:
        return "Borderline"

def tq_to_text(score):
    if score == 1:
        return 'Poor'
    elif score == 2:
        return 'Marginal'
    elif score == 3:
        return 'Good'
    else:
        return 'Undetermined'


def fill_ischemia_line(doc, summary):
    imp_score = 0
    if 'Impression' in summary['positive']:
        imp_score = summary['positive']['Impression']
    elif 'Impression' in summary['negative']:
        imp_score = summary['negative']['Impression']
    imp = impression_to_text(imp_score)
    doc.set_font('times', '', 10)
    doc.cell(text=imp)

    cat = str(summary['category'])
    if cat == 'N/A':
        cat = "0"
    doc.set_font('times', 'B', 10)
    doc.cell(text='Category:')
    doc.set_font('times', '', 10)
    doc.cell(text=cat)

    ischemia = "None detected"
    if 'Global Ischemia' in summary['positive']:
        ischemia = "Global Ischemia detected"
    elif 'Local Ischemia' in summary['positive']:
        ischemia = "Local Ischemia detected"
    elif 'Global Ischemia (borderline)' in summary['positive']:
        ischemia = "Borderline Global Ischemia detected"
    elif 'Local Ischemia (borderline)' in summary['positive']:
        ischemia = "Borderline Local Ischemia detected"
    doc.set_font('times', 'B', 10)
    doc.cell(text='Ischemia:')
    doc.set_font('times', '', 10)
    doc.cell(text=ischemia)

    severity = "N/A"
    if 'Ischemic Disease Severity' in summary['positive']:
        severity = str(summary['positive']['Ischemic Disease Severity'])
    doc.set_font('times', 'B', 10)
    doc.cell(text='Severity:')
    doc.set_font('times', '', 10)
    doc.cell(text=severity)

def fill_primary_results(doc, summary, info={}):
    doc.add_page()
    doc.set_font('times', 'B', 14)
    doc.cell(text='MCG Analysis Results', new_x="LMARGIN", new_y="NEXT", align='C')

    doc.set_font('times', 'B', 12)
    doc.cell(20, 10, 'Ischemia Results')
    doc.ln()
    doc.set_font('times', '', 10)
    fill_ischemia_line(doc, summary)
    doc.ln()

    doc.set_font('times', 'B', 12)
    doc.cell(10, 10, 'Positive Results')
    doc.ln()
    doc.set_font('times', '', 10)
    for name in sorted(list(summary['positive'].keys())):
        score = summary['positive'][name]
        doc.cell(text="%s (%0.1f)" % (name, score))
        doc.ln()

    doc.set_font('times', 'B', 12)
    doc.cell(10, 10, 'Negative Results')
    doc.set_font('times', '', 10)
    doc.ln()
    for name in sorted(list(summary['negative'].keys())):
        doc.cell(text=name)
        doc.ln()

def add_sample_results(doc, samp):
    doc.add_page()
    doc.set_font('times', 'B', 14)
    doc.cell(text="Sample %s (Quality %s) %s" % (samp["input"], tq_to_text(samp['results']['tracing-quality']), samp["timestamp"]), new_x="LMARGIN", new_y="NEXT", align='C')

    doc.set_font('times', 'B', 12)
    doc.cell(text='Results')
    doc.ln()
    doc.set_font('times', '', 10)
    # FIXME: pandas
    for name, h in samp['results'].items():
        if name == 'tracing-quality':
            continue
        pos = '-'
        if h['positive']:
            pos = '+'

        doc.cell(text="[%s] %s : %s" % (pos, name, str(h['value'])))
        doc.ln()

    # Plot DSP transforms
    doc.add_page()
    doc.set_font('times', 'B', 14)
    doc.cell(text="Sample %s (Quality %s) %s" % (samp["input"], tq_to_text(samp['results']['tracing-quality']), samp["timestamp"]), new_x="LMARGIN", new_y="NEXT", align='C')

    doc.set_font('times', 'B', 12)
    doc.cell(text='DSP Transforms')
    doc.ln()
    doc.set_font('times', '', 10)

    num_plots = len(samp['transforms'])
    num_col = 2
    if num_plots % 2 == 1:
        num_col = 3
    num_row = int(num_plots / num_col)
    fig = Figure(figsize=(num_row, num_col), dpi=1000)
    idx = 1
    for key in sorted(list(samp['transforms'].keys())):
        ax = fig.add_subplot(num_row, num_col, idx)
        ax.set_title(key, fontsize=4)
        data = samp['transforms'][key]
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.plot(data, color="blue", lw=0.5)
        idx += 1
    # FIXME: improve plotting
    canvas = FigureCanvas(fig)
    canvas.draw()
    img = Image.fromarray(np.asarray(canvas.buffer_rgba()))
    doc.image(img, w=doc.epw)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    if (res['object-type'] != 'analysis-result') or ('results' not in res):
        print("Invalid JSON AnalysisResults object!")
        sys.exit()

    doc = create_pdf(res)

    # Generate official, aggregate/overall results
    summary = res['results']
    fill_primary_results(doc, summary)

    # Generate detailed, per-sample results
    report_samples = [ ]
    for att in res['attachments']:
        if att['name'] == 'report':
            # replace JSON-encoded string with decoded object
            if att['mime-type'] == "application/json":
                att['mime-type'] = "application/x-java-object"
                att['data'] = json.loads(att['data'])
            report_samples = att['data']

    for samp in report_samples:
        add_sample_results(doc, samp)

    doc.output("mcg-analysis-result.pdf")

