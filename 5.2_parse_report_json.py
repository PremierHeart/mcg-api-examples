#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import base64

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

def impression_label(score):
    if score <= 1:
        return "Normal"
    elif score > 4:
        return "Abnormal"
    else:
        return "Borderline"

def print_report_attachment(summary, att):
    imp_score = 0
    if 'Impression' in summary['positive']:
        imp_score = summary['positive']['Impression']
    elif 'Impression' in summary['negative']:
        imp_score = summary['negative']['Impression']
    print("Impression: %s" % impression_label(imp_score))
    cat = str(summary['category'])
    if cat == 'N/A':
        cat = "0"
    print("Category: %s" % cat)
    severity = "N/A"
    if 'Ischemic Disease Severity' in summary['positive']:
        severity = str(summary['positive']['Ischemic Disease Severity'])
    print("Severity: %s" % severity)
    #fill_ischemia_line(doc, summary)
    # ischemia
    ischemia = "None detected"
    if 'Global Ischemia' in summary['positive']:
        ischemia = "Global Ischemia detected"
    elif 'Local Ischemia' in summary['positive']:
        ischemia = "Local Ischemia detected"
    elif 'Global Ischemia (borderline)' in summary['positive']:
        ischemia = "Borderline Global Ischemia detected"
    elif 'Local Ischemia (borderline)' in summary['positive']:
        ischemia = "Borderline Local Ischemia detected"
    print("Ischemia: %s" % ischemia)
    # 2-ry/3-ary
    print("Positive Diagnoses:")
    for name in sorted(list(summary['positive'].keys())):
        score = summary['positive'][name]
        print("\t%s (%0.1f)" % (name, score))
    print("Negative Diagnoses:")
    for name in sorted(list(summary['negative'].keys())):
        print("\t%s" % name)
    #
    data = retrieve_attachment(att)
    # data is a list of per-input resultd
    for rec in data:
        print(rec.keys())
        print("[%d] %s %s" % (rec['index'], rec['input'], rec['timestamp']))
        print("Diagnoses:")
        for name, h in rec['results'].items():
            if isinstance(h, dict):
                pos = '+' if h['positive'] else '-'
                print("\t[%s] %s : %s" % (pos, name, str(h['value'])))
            else:
                print("\t%s : %s" % (name, str(h)))
        print("Transforms:")
        for name, arr in rec['transforms'].items():
            print("%s : %d" % (name, len(arr)))

    #summary = res['results']
    #fill_primary_results(doc, summary)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    for idx, att in enumerate(res['attachments']):
        if att['output'] == 'report-json' and att['name'] == 'report':
            print_report_attachment(res['results'], att)
