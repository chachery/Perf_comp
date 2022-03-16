#!/usr/bin/bash

#@argv
#argv1:result_store_path	The path to store output files.
#argv2:test_lib_path	The path where stores test lib files which after filtering.

#result file
EPANG_RESULT=$1/epang_result.csv
RAPPAS_RESULT=$1/rappas_result.csv
APPLES_RESULT=$1/apples_result.csv
VSEARCH_RESULT=$1/vsearch_result.csv
HSBLASTN_RESULT=$1/hsblastn_result.csv

#test lib path & file
TEST_QUERY=$2/test_query.fasta
TEST_QUERY_ME=$2/test_query_me.fasta

#to make result_store_path
if [ ! -d $1 ];then
    mkdir $1
fi

#do classifications
sh classify.sh -i $TEST_QUERY -o $EPANG_RESULT -j 1 -E -l $2 -U
sh classify.sh -i $TEST_QUERY -o $RAPPAS_RESULT -j 2 -E -l $2 -U
sh classify.sh -i $TEST_QUERY -o $APPLES_RESULT -j 3 -E -l $2 -U
sh classify.sh -i $TEST_QUERY -o $VSEARCH_RESULT -j 5 -E -l $2
sh classify.sh -i $TEST_QUERY -o $HSBLASTN_RESULT -j 6 -E -l $2

#exam
python -c "from pys import exam; exam.doExam('$1')"
