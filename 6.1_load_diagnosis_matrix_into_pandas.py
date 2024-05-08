#!/usr/bin/env python
# (c) Copyright 2023 Premier Heart, LLC

import sys
import json
import numpy as np
import pandas as pd

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
        print("---DIAGNOSIS MATRIX---")
        df = pd.DataFrame(summary['diagnosis-matrix'])
        pd.options.display.max_columns = None
        print(df.describe(include=np.number))

