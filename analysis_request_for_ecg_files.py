#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import json
import os
import random
import sys
from datetime import datetime

def build_request(inputs):
    return {
      "object-type": "analysis-request",
      #"analysis": {
      #  "type": "ecg-phase",
      #  "options": {},
      #},
      #"output": { 
      #    "signal-phase-portrait": {
      #    },
      #    "transform-json": {
      #      'in-place-json': True
      #  }
      #},
      "analysis": {
        "type": "mcg-aggregate",
        "options": {
          "diagnosis-matrix": True
        }
      },
      "output": { }, # see multiple_output_request for attachment handling
      "input": inputs,
      "comment": "(FAKE DATA) Generated by " + os.path.basename(__file__)
    }

def input_for_ecg_json(json_str, age=40, gender='M'):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
      "type": "ecg",
      "format": "json",
      "timestamp": ts,
      "age": age,
      "gender": gender,
      "data": json.loads(json_str)
    }

if __name__ == '__main__':
    inputs = [ ]
    for x in range(3):
        fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', ("ecg_%d.json" % (x+1)))
        with open(fname, 'r') as f:
            inputs.append(input_for_ecg_json(f.read()))

    data = build_request( inputs )
    print(json.dumps(data))
    
