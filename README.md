# mcg-api-examples
Examples for connecting to the MCG API taken from the API Getting Started manual

(c) Copyright 2023 Premier Heart, LLC


### Basic API Connectivity

* simple_connection.py - Tests that a connection can be made to the API server
```
bash# MCG_API_TOKEN_FILE='.token/mcg_api_jwt.dat' python simple_connection.py
Connecting to unused endpoint. Should print 'ERROR /':
ERROR /
```

* error_handling.py - Demonstrates how to handle various connection errors
```
bash# MCG_API_TOKEN_FILE='.token/mcg_api_jwt.dat' python error_handling.py
[01] Connecting to invalid server
 ... Caught exception
[02] Connecting to invalid path
 ... Caught 401 error
[03] Connecting with empty token
 ... Caught 401 error
[04] Connecting with invalid token
 ... Caught 401 error
[05] Connecting with bad/expired token
 ... Caught 401 error
[06] Connecting with valid token and empty request
 ... Caught error 'API request error': Missing 'analysis' in request 
[07] Connecting with valid token and incorrect type
 ... Caught error 'API request error': Unsupported object type 'MyBrokenType 
[08] Connecting with valid token and invalid request
 ... Caught error 'API request error': Missing 'input' in request 
[09] Connecting with valid token and empty request input
 ... Caught error 'Insufficient input data provided': 1+ inputs required 
[10] Connecting with valid token and invalid request input
 ... Caught error 'API request error': Unsupported object type 'MyBrokenType 
[11] Connecting with valid token and invalid analysis type
 ... Caught error: Extension not found
```    

* basic_analysis_request.py - Demonstrates how to send an AnalysisRequest to the API server. This uses random data for the ECG inputs, which may result in an Error object being returned instead of an AnalysisResult.
```
bash# MCG_API_TOKEN_FILE='.token/mcg_api_jwt.dat' python basic_analysis_request.py
Analysis Results:
	object-type: analysis-result
	locale: en-US
	encoding: utf-8
	framework: {'name': 'BSIA', 'version': '1.0.1', 'description': 'BioSignal Information Analysis framework', 'notice': 'Experimental software: NOT FOR CLINICAL USE. (c) Copyright 2022 Premier Heart, LLC'}
	id: None
	results: {'source': 'mcg-avg', 'sample': '2', 'category': 'N/A', 'positive':
/* ... OMITTED ... */
}]'}]
	warnings: []
```

* send_ecg_files.py - Demonstrates how to send ECG JSON files for analysis and display the results.
```
bash# MCG_API_TOKEN_FILE='.token/mcg_api_jwt.dat' python send_ecg_files.py
Read input: /home/ph/projects/mcg-api-examples/data/ecg_1.json
Read input: /home/ph/projects/mcg-api-examples/data/ecg_2.json
Read input: /home/ph/projects/mcg-api-examples/data/ecg_3.json
Results Summary:
	object-type: analysis-result
	locale: en-US
	encoding: utf-8
	framework: {'name': 'BSIA', 'version': '1.0.1', 'description': 'BioSignal Information Analysis framework', 'notice': 'Experimental software: NOT FOR CLINICAL USE. (c) Copyright 2022 Premier Heart, LLC'}
	id: None
	Diagnosis generated by mcg-avg using input 2 as a representative sample
	MCG Category: N/A
	Conditions detected (positives):
		Impression : 5.0
		Disease Severity : 6.5
/* ... OMITTED ... */
	Tracing Quality:
		0 : 90
		1 : 90
		2 : 90
	warnings: []
Attachments:
```
* multiple_output_request.py - Demonstrates how to request multiple output files, which will be included in the AnalysisResults object as attachments.
```
bash# MCG_API_TOKEN_FILE='.token/mcg_api_jwt.dat' python multiple_output_request.py
Read input: /home/ph/projects/mcg-api-examples/data/ecg_1.json
Read input: /home/ph/projects/mcg-api-examples/data/ecg_2.json
Read input: /home/ph/projects/mcg-api-examples/data/ecg_3.json
Results Summary:
	object-type: analysis-result
	locale: en-US
	encoding: utf-8
	framework: {'name': 'BSIA', 'version': '1.0.1', 'description': 'BioSignal Information Analysis framework', 'notice': 'Experimental software: NOT FOR CLINICAL USE. (c) Copyright 2022 Premier Heart, LLC'}
	id: None
	Diagnosis generated by mcg-avg using input 2 as a representative sample
	MCG Category: N/A
	Conditions detected (positives):
		Impression : 5.0
		Disease Severity : 6.5
/* ... OMITTED ... */
	Tracing Quality:
		0 : 90
		1 : 90
		2 : 90
	warnings: []
Attachments:
	[0] result-group from result-json for input '1' : application/x-java-object (in-memory JSON object)
	[1] result-sample from result-json for input '0' : application/x-java-object (in-memory JSON object)
	[2] result-sample from result-json for input '1' : application/x-java-object (in-memory JSON object)
	[3] result-sample from result-json for input '2' : application/x-java-object (in-memory JSON object)
	[4] result-explain-group from result-explain-json for input '1' : application/x-java-object (in-memory JSON object)
	[5] result-explain-sample from result-explain-json for input '0' : application/x-java-object (in-memory JSON object)
	[6] result-explain-sample from result-explain-json for input '1' : application/x-java-object (in-memory JSON object)
	[7] result-explain-sample from result-explain-json for input '2' : application/x-java-object (in-memory JSON object)
	[8] feature-group from feature-json for input '1' : application/x-java-object (in-memory JSON object)
	[9] feature-sample from feature-json for input '0' : application/x-java-object (in-memory JSON object)
	[10] feature-sample from feature-json for input '1' : application/x-java-object (in-memory JSON object)
	[11] feature-sample from feature-json for input '2' : application/x-java-object (in-memory JSON object)
	[12] transform-sample from transform-json for input '0' : application/x-java-object (in-memory JSON object)
	[13] transform-sample from transform-json for input '1' : application/x-java-object (in-memory JSON object)
	[14] transform-sample from transform-json for input '2' : application/x-java-object (in-memory JSON object)
	[15] transform-heatmap-amp.V5 from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 104719-byte file)
	[16] transform-heatmap-amp.II from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 104635-byte file)
	[17] transform-heatmap-aps.V5 from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 113311-byte file)
	[18] transform-heatmap-aps.II from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 112693-byte file)
	[19] transform-heatmap-ccr.(V5,II) from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 156335-byte file)
	[20] transform-heatmap-coh.(V5,II) from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 54395-byte file)
	[21] transform-heatmap-imr.(V5,II) from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 107149-byte file)
	[22] transform-heatmap-psa.(V5,II) from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 76549-byte file)
	[23] transform-heatmap-xar.(V5,II) from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 66321-byte file)
	[24] transform-heatmap-cps.(V5,II) from transform-heatmap for input '0,1,2' : image/svg+xml (base64-encoded 113602-byte file)
	[25] report from report-json for input '0,1,2' : application/x-java-object (in-memory JSON object)
```
* tracing_quality_request.py - Demonstrates how to perform an ECG Tracing Quality analysis
```
bash# MCG_API_TOKEN_FILE='.token/mcg_api_jwt.dat' python tracing_quality_request.py
Read input: /home/ph/projects/mcg-api-examples/data/ecg_1.json
Read input: /home/ph/projects/mcg-api-examples/data/ecg_2.json
Read input: /home/ph/projects/mcg-api-examples/data/ecg_3.json
Results Summary:
	object-type: analysis-result
	locale: en-US
	encoding: utf-8
	framework: {'name': 'BSIA', 'version': '1.0.1', 'description': 'BioSignal Information Analysis framework', 'notice': 'Experimental software: NOT FOR CLINICAL USE. (c) Copyright 2022 Premier Heart, LLC'}
	id: None
	Tracing Quality: 90
		**  Baseline: 100 Noise: 90 Range: 99
		V5  Baseline: 100 Noise: 90 Range: 99
		II  Baseline: 100 Noise: 100 Range: 100
	ECG Details:
		V5  Count: 8192  High: 2384  Low: 128  Baseline: 787  Total: 6447252  Peak Count: 753  Voltage: 5.64  PPV: 2256
		II  Count: 8192  High: 1841  Low: 193  Baseline: 693  Total: 5681463  Peak Count: 567  Voltage: 4.12  PPV: 1648
	warnings: []
```

### Analysis of API Output
These programs take an AnalysisResults JSON file as in put. In the following examples, the automatically-saved output of multiple_output_request.py has been used.

* analyze_result_diagnoses.py - This demonstrates how to load the contents of the Diagnosis Matrix and of **results-json** attachments into a Pandas dataframe. For each dataframe, a summary is printed and a histogram is plotted. Note that the contents of **results-json** are for research purposes only, and should not be interpreted without guidance from Premier Heart staff.
```
bash# python analyze_result_diagnoses.py data/analysis-results.multiple-outputs.example.json
DIAGNOSIS MATRIX:
  id Impression (text) Ischemia  Disease Severity  Ischemic Disease Severity  \
0  0          Abnormal                        6.5                        0.0   
1  1          Abnormal                        6.5                        0.0   
2  2          Abnormal                        6.5                        0.0   
/* ... OMITTED ... */
INPUT 0
        (mcg-pre) MCG Preliminary Analysis Algorithm
                - (HR) Heart Rate : 65
                + (rA) Ventricular Hypertrophy (raw) : 0.16
                + (A) Ventricular Hypertrophy : 0.16
                + (rC) Ischemia (raw) : 0.18
                + (C) Ischemia : 0.21
/* ... OMITTED ... */
				 MCG Ischemia Analysis
   CAD1  CAD2  CAD3  CAD4  CAD5  CAD6  CAD7  CAD8  CAD9  CAD10  CAD11  CAD12  \
0     1     0     0     0     0     0     0     0     0      0      0      0
1     1     0     0     0     0     0     0     0     0      0      0      0
2     1     0     0     0     0     0     0     0     0      0      0      0

   CAD13  CAD14  NCI1  NCI2  NCI3  NCI4  NCI5  NCI6  NCI7  NCI8  NCI9  NCI10  \
0      0      0     0     0     0     0     0     0     0     0     0      0
1      0      0     0     0     0     0     0     0     0     0     0      0
2      0      0     0     0     0     0     0     0     0     0     0      0

   NCI11  NCI12  NCI13  NCI14  NCI15  NCI  CAD  C
0      0      0      0      0      0    0    1  1
1      0      0      0      0      0    0    1  1
2      0      0      0      0      0    0    1  1
       CAD1  CAD2  CAD3  CAD4  CAD5  CAD6  CAD7  CAD8  CAD9  CAD10  CAD11  \
count   3.0   3.0   3.0   3.0   3.0   3.0   3.0   3.0   3.0    3.0    3.0
mean    1.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0    0.0    0.0
std     0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0    0.0    0.0
min     1.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0    0.0    0.0
25%     1.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0    0.0    0.0
50%     1.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0    0.0    0.0
75%     1.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0    0.0    0.0
max     1.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0    0.0    0.0

       CAD12  CAD13  CAD14  NCI1  NCI2  NCI3  NCI4  NCI5  NCI6  NCI7  NCI8  \
count    3.0    3.0    3.0   3.0   3.0   3.0   3.0   3.0   3.0   3.0   3.0
mean     0.0    0.0    0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0
std      0.0    0.0    0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0
min      0.0    0.0    0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0
25%      0.0    0.0    0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0
50%      0.0    0.0    0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0
75%      0.0    0.0    0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0
max      0.0    0.0    0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0

       NCI9  NCI10  NCI11  NCI12  NCI13  NCI14  NCI15  NCI  CAD    C
count   3.0    3.0    3.0    3.0    3.0    3.0    3.0  3.0  3.0  3.0
mean    0.0    0.0    0.0    0.0    0.0    0.0    0.0  0.0  1.0  1.0
std     0.0    0.0    0.0    0.0    0.0    0.0    0.0  0.0  0.0  0.0
min     0.0    0.0    0.0    0.0    0.0    0.0    0.0  0.0  1.0  1.0
25%     0.0    0.0    0.0    0.0    0.0    0.0    0.0  0.0  1.0  1.0
50%     0.0    0.0    0.0    0.0    0.0    0.0    0.0  0.0  1.0  1.0
75%     0.0    0.0    0.0    0.0    0.0    0.0    0.0  0.0  1.0  1.0
max     0.0    0.0    0.0    0.0    0.0    0.0    0.0  0.0  1.0  1.0
MCG Disease Severity Analysis
/* ... OMITTED ... */
```
![Diagnosis Matrix histogram](images/diagnosis-matrix-df-histogram.png?raw=true "Diagnosis Matrix histogram")
![Ischemia Algorithm histogram](images/ischemia-df-histogram.png?raw=true "Ischemia histogram")

* analyze_result_transforms.py - Demonstrates how to load the contents of **transform-json** into a Pandas dataframe. As an example analysis, the Frequency Response of lead II is calculated. 
```
bash# python analyze_result_transforms.py   data/analysis-results.multiple-outputs.example.json
(aps) auto power spectrum of Signal V5
      frequency domain: power peaks in signal
           0         1          2    ...       125  126       127
count      3.0  3.000000   3.000000  ...  3.000000  3.0  3.000000
mean   32765.0  4.000000  11.666667  ...  2.666667  2.0  1.333333
std        0.0  2.645751   3.214550  ...  0.577350  0.0  0.577350
min    32765.0  2.000000   8.000000  ...  2.000000  2.0  1.000000
25%    32765.0  2.500000  10.500000  ...  2.500000  2.0  1.000000
50%    32765.0  3.000000  13.000000  ...  3.000000  2.0  1.000000
75%    32765.0  5.000000  13.500000  ...  3.000000  2.0  1.500000
max    32765.0  7.000000  14.000000  ...  3.000000  2.0  2.000000

[8 rows x 128 columns]

(aps) auto power spectrum of Signal II
      frequency domain: power peaks in signal
/* ... OMITTED ... */
Frequency Response (II):
            0    1    2    3    ...         124   125        126  127
count  3.000000  3.0  3.0  3.0  ...    3.000000   3.0   3.000000  3.0
mean   2.764980  0.0  0.0  0.0  ...  326.200515  15.0   3.333333  0.0
std    0.002138  0.0  0.0  0.0  ...   23.721900   4.0   5.773503  0.0
min    2.762648  0.0  0.0  0.0  ...  299.130435  11.0   0.000000  0.0
25%    2.764047  0.0  0.0  0.0  ...  317.620773  13.0   0.000000  0.0
50%    2.765446  0.0  0.0  0.0  ...  336.111111  15.0   0.000000  0.0
75%    2.766146  0.0  0.0  0.0  ...  339.735556  17.0   5.000000  0.0
max    2.766847  0.0  0.0  0.0  ...  343.360000  19.0  10.000000  0.0

[8 rows x 128 columns]  
```

### Advanced Analysis Types
* differential_analysis_request.py
* diagnosis_trace.py

### Displaying API output
* extract-transform-heatmaps.py
* transform_heatmap_output.py
* transform_topo_plot.py
* generate_pdf_report.py
