#!/usr/bin/python
#Type "python setup_filter.py fasta_file taxon_file (BOLD_file)"
#taxon_file is made with "taxonkit list --show-rank --show-name --indent " " --ids xxxx"
import sys
import os

import config
from pys import species_separater
from pys.colorfulWriter import warning_writer, error_writer, log_writer, log_w
from pys.seq_filter import intra_sp_filter_all, inter_sp_filter, getAbundance

###sys.argv
log = "log"
os.system('>' + log)
list_argv = sys.argv
log_w('File '+list_argv[1]+':\n')
len_list_argv = len(sys.argv)-1
if len_list_argv < 2:
    error_writer('Insufficient parameters! Please type "python setup.py fasta_file taxon_file (BOLD_file)"')
elif len_list_argv == 2:
    BOLD_f = "null"
elif len_list_argv == 3:
    BOLD_f = list_argv[3]
else:
    error_writer('Too many parameters! Please type "python setup.py fasta_file taxon_file (BOLD_file)"')

###Variables
input_f = sys.argv[1]
taxon_f = sys.argv[2]
ls=os.listdir(os.getcwd())
cp_input_f='copy_'+input_f

#dic_config = {}
threshold_sp_pro = config.threshold_sp_pro
threshold_sp_con = config.threshold_sp_con
threshold_inter = config.threshold_inter
bar_type = config.barcoding_type
IS_TRIM = config.IS_TRIM
REF_HS = config.REF_HS
SIMILARITY_THRESHOLD_HS = config.SIMILARITY_THRESHOLD_HS
COVERAGE_THRESHOLD_HS = config.COVERAGE_THRESHOLD_HS

#percentage_sp_con =config.percentage_sp_con

sp_dist = "dist/sp_dist/"
sp_dist_all = "dist/sp_dist/*"
output_f_name = "dist_"+input_f
output_f = "dist/"+output_f_name
high_simi_dir = "dist/high_simi/"
high_simi_dir_all = "dist/high_simi/*"
hs_lib_dir = "dist/hs_lib/"
hs_lib_dir_all = "dist/hs_lib/*"


###Check
#Check fasta file
if not input_f in ls:
    error_writer('Fasta file not be found!')

if not '.fa' in input_f:
    error_writer('It is not a fasta file!')

#Check taxon file
if not taxon_f in ls:
    error_writer('Taxon file not be found!')

###Pre
os.system('rm -rf ' + sp_dist_all)
os.system('rm -rf ' + high_simi_dir_all)
os.system('rm -rf ' + hs_lib_dir_all)
os.system('>' + output_f)
os.system('seqkit seq -w 0 '+input_f+' > '+cp_input_f)
os.system('sed -i -e "s/:/_/g" -e "s/\'//g" '+cp_input_f)

###Species separater
#a dic stored with {genus:(family,order,clazz)}
dic_gR = species_separater.speciesSeparater(cp_input_f, taxon_f, BOLD_f, sp_dist, hs_lib_dir, bar_type, REF_HS, SIMILARITY_THRESHOLD_HS, COVERAGE_THRESHOLD_HS, IS_TRIM)
dic_abundance = getAbundance(sp_dist)
intra_sp_filter_all(sp_dist, dic_gR, threshold_sp_pro, threshold_sp_con)
inter_sp_filter(output_f, dic_abundance, sp_dist, high_simi_dir, threshold_inter)

###Post
log_writer("Filtering finished!!!")
os.system('rm -rf result.COI')
os.system('rm -rf hs.COI')
#os.system('rm -rf ' + sp_dist_all)
