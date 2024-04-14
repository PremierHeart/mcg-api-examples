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

def get_impression(summary):
    score = 0
    if 'Impression' in summary['positive']:
        score = summary['positive']['Impression']
    elif 'Impression' in summary['negative']:
        score = summary['negative']['Impression']

    if score <= 1:
        return "Normal"
    elif score > 4:
        return "Abnormal"
    else:
        return "Borderline"

def get_mcg_category(summary):
    cat = str(summary['category'])
    if cat == 'N/A':
        cat = "0"
    return cat

def get_ischemia(summary):
    ischemia = "None detected"
    if 'Global Ischemia' in summary['positive']:
        ischemia = "Global Ischemia detected"
    elif 'Local Ischemia' in summary['positive']:
        ischemia = "Local Ischemia detected"
    elif 'Global Ischemia (borderline)' in summary['positive']:
        ischemia = "Borderline Global Ischemia detected"
    elif 'Local Ischemia (borderline)' in summary['positive']:
        ischemia = "Borderline Local Ischemia detected"
    return ischemia

def print_primary_results(summary):
    print("Primary results")
    print("\tImpression: %s" % get_impression(summary))
    print("\tCategory: %s" % get_mcg_category(summary))

    severity = "N/A"
    if 'Ischemic Disease Severity' in summary['positive']:
        severity = str(summary['positive']['Ischemic Disease Severity'])
    print("\tSeverity: %s" % severity)
    print("Ischemia: %s" % get_ischemia(summary))

    print("Positive Diagnoses:")
    for name in sorted(list(summary['positive'].keys())):
        score = summary['positive'][name]
        print("\t%s (%0.1f)" % (name, score))

    print("Negative Diagnoses:")
    for name in sorted(list(summary['negative'].keys())):
        print("\t%s" % name)

def print_report_attachment(summary, att):
    print_primary_results(summary)

    print("Supporting results:")
    data = retrieve_attachment(att)
    # report-json attachment data is a list of per-input results
    for rec in data:
        print("\t[%d] \"%s\" %s" % (rec['index'], rec['input'], rec['timestamp']))
        print("\t[%d] Diagnoses:" % rec['index'])
        for name, h in rec['results'].items():
            if isinstance(h, dict):
                pos = '+' if h['positive'] else '-'
                print("\t\t[%s] %s : %s" % (pos, name, str(h['value'])))
            else:
                print("\t\t%s : %s" % (name, str(h)))
        print("\t[%d] Transforms:" % rec['index'])
        for name, arr in rec['transforms'].items():
            print("\t\t%s : %d" % (name, len(arr)))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Missing AnalysisResults.json argument!"

    with open(sys.argv[1]) as f:
        res = json.loads(f.read())

    for idx, att in enumerate(res['attachments']):
        if att['output'] == 'report-json' and att['name'] == 'report':
            print_report_attachment(res['results'], att)
