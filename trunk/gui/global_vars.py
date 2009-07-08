# PopGen 1.0 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand 
# Copyright (C) 2009, Arizona State University
# See PopGen/License

import sys

if sys.platform.startswith('win'):
    DATA_DOWNLOAD_LOCATION = "C:/PopGen/data"
else:
    DATA_DOWNLOAD_LOCATION = "../PopGen/data"
IPF_TOLERANCE = 0.0001
IPF_MAX_ITERATIONS = 250
IPU_TOLERANCE = 0.0001
IPU_MAX_ITERATIONS = 50
SYNTHETIC_POP_MAX_DRAWS = 25
SYNTHETIC_POP_PVALUE_TOLERANCE = 0.9999
ROUNDING_PROCEDURE = 'arithmetic'
RAW_SUMMARY_FILES = ['geo_uf3.zip', '00001_uf3.zip', '00004_uf3.zip', '00006_uf3.zip']
RAW_SUMMARY_FILES_NOEXT = ['geo', '00001', '00004', '00006']
RAW_SUMMARY_FILES_COMMON_VARS = ['fileid', 'stusab', 'chariter', 'cifsn', 'logrecno']
RAW_SUMMARY_FILES_COMMON_VARS_TYPE = ['text', 'text', 'int', 'int', 'int']
MASTER_SUMMARY_FILE_VARS = ['state', 'county', 'tract', 'bg', 'sumlev', 'logrecno']
HOUSING_SUMMARY_TABLES = [9, 10, 14, 52]
PERSON_SUMMARY_TABLES = [6, 8, 43]
