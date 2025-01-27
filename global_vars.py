# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand 
# Copyright (C) 2009, Arizona State University
# See PopGen/License

import sys

if sys.platform.startswith('win'):
    DATA_DOWNLOAD_LOCATION = "C:/PopGen/data"
else:
    DATA_DOWNLOAD_LOCATION = "../PopGen/data"

HACS_VARCOUNT = 189
PACS_VARCOUNT = 238

HACS5yr_VARCOUNT = 189
PACS5yr_VARCOUNT = 222


IPF_TOLERANCE = 0.0001
IPF_MAX_ITERATIONS = 250
IPU_TOLERANCE = 0.0001
IPU_MAX_ITERATIONS = 50
SYNTHETIC_POP_MAX_DRAWS = 25
SYNTHETIC_POP_PVALUE_TOLERANCE = 0.9999
ROUNDING_PROCEDURE = 'bucket'

RAW_SUMMARY2000_FILES = ['geo_uf3.zip', '00001_uf3.zip', '00004_uf3.zip',
                         '00005_uf3.zip', '00006_uf3.zip',
                         '00056_uf3.zip', '00058_uf3.zip']
RAW_SUMMARY2000_FILES_NOEXT = ['geo', '00001', '00004', '00005',
                               '00006', '00056', '00058']

RAW_SUMMARYACS_FILES = ['g20073%s.txt', 
                        '20073%s0011000.zip', '20073%s0013000.zip', '20073%s0014000.zip', 
                        '20073%s0015000.zip', '20073%s0046000.zip',
                        '20073%s0048000.zip', '20073%s0082000.zip',
                        '20073%s0103000.zip',
                        '20073%s0109000.zip', '20073%s0130000.zip',
                        '20073%s0133000.zip',
                        '20073%s0140000.zip']

RAW_SUMMARYACS_FILES_NOEXT = ['geo', '0011', '0013', '0014', '0015', 
                              '0046','0048', '0082', '0103', '0109',
                              '0130','0133', '0140']


RAW_SUMMARYACS5yr_FILES_NOEXT = ['geo', '0010', '0011', '0012', '0033', '0030', '0031', 
                              '0053','0069', '0096', '0104']


RAW_SUMMARYACS5yr_FILES = ['g20095%s.txt', '20095%s0010000.txt',
                        '20095%s0011000.txt', '20095%s0012000.txt', '20095%s0033000.txt', '20095%s0030000.txt', '20095%s0031000.txt', 
                        '20095%s0053000.txt', '20095%s0069000.txt',
                        '20095%s0096000.txt', 
                        '20095%s0102000.txt', '20095%s0104000.txt']



RAW_SUMMARY2000_FILES_COMMON_VARS = ['fileid', 'stusab', 'chariter', 'cifsn', 'logrecno']
RAW_SUMMARY2000_FILES_COMMON_VARS_TYPE = ['text', 'text', 'int', 'int', 'int']
MASTER_SUMMARY_FILE_VARS = ['state', 'county', 'tract', 'bg', 'sumlev', 'geocomp', 'logrecno']


RAW_SUMMARYACS_FILES_COMMON_VARS = ['fileid', 'filetype', 'stusab', 'chariter', 'cifsn', 'logrecno']
RAW_SUMMARYACS_FILES_COMMON_VARS_TYPE = ['text', 'text', 'text', 'int', 'int', 'int']


