#!/usr/bin/python

###Barcoding type(eg: all, COI, 16S, 18S)
barcoding_type = "all"

###Intra-species filter
#Similarity threshold that determining sequences as the same species
#To get a sequence with highest score: score = num_of_pro + num2_of_con * 2
#Progressive
threshold_sp_pro = 0.95
#Conservative
threshold_sp_con = 0.90

###Inter-species filter
#Similarity threshold that determining sequences as the same species
threshold_inter = 0.97

###Filter with similarity and coverage rate according to the reference
#Reference file
REF_HS = "Collembola_COI_ref.fas"
#Similarity threshold
SIMILARITY_THRESHOLD_HS = 70.0
#Coverage threshold
COVERAGE_THRESHOLD_HS = 80.0
#Trim swith
IS_TRIM = True
