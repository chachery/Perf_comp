#!/usr/bin/bash
#Type "sh doPick.sh $lib_path $test_lib_path $pick_times"

#@argv
#argv1:lib_path		The path where stores lib files.
#argv2:test_lib_path	The path where stores test lib files which after filtering.
#argv3:pick_times	The num of seqs picked from lib files.

#common path
COMMON_PATH=$(pwd)

#lib path & file
#LIB_PATH=$COMMON_PATH/lib/Collembola_COI
LIB_PATH=$COMMON_PATH/$1
LIB_1=$LIB_PATH/lib.fasta
LIB_2=$LIB_PATH/lib_pp.fasta
LABEL=$LIB_PATH/name.label 

#test lib path & file
TEST_LIB_PATH=$COMMON_PATH/$2
TEST_QUERY=$TEST_LIB_PATH/test_query.fasta
TEST_REF=$TEST_LIB_PATH/test_ref.fasta
#TEST_QUERY_ME=$TEST_LIB_PATH/test_query_me.fasta
#TEST_REF_ME=$TEST_LIB_PATH/test_ref_me.fasta
TEST_VREF=$TEST_LIB_PATH/test_vref.fasta
TEST_LABEL=$TEST_LIB_PATH/test.label
TEST_TREE=$TEST_LIB_PATH/test_ref.nwk
TEST_TREE_ME=$TEST_LIB_PATH/test_ref_me.nwk
TEST_BLATN_PATH=$TEST_LIB_PATH/hs-blastn/


if [ ! -d $2 ];then
    mkdir $2
fi

#random pick
python -c "from pys2 import random_pick; random_pick.r_pick('$LIB_2','$TEST_REF','$TEST_QUERY','$3')"

#label filter
python -c "from pys2 import label_filter; label_filter.label_filter('$LABEL','$TEST_LABEL','$TEST_QUERY')"

#syn vsearch
python -c "from pys2 import syn_vsearch; syn_vsearch.syn('$LIB_1','$TEST_QUERY','$TEST_VREF')"

#syn hs-blastn
mkdir $TEST_BLATN_PATH && cp $TEST_VREF $TEST_BLATN_PATH && cd $TEST_BLATN_PATH && hs-blastn index test_vref.fasta && cd -

#build tree with FastTree
FastTree -gtr -nt < $TEST_REF > $TEST_TREE
FastTreeMP -nosupport -nt -nome -noml -intree $TEST_TREE < $TEST_REF > $TEST_TREE_ME

#cp $TEST_QUERY $TEST_QUERY_ME
#cp $TEST_REF $TEST_REF_ME
#python pys2/toSynTestLib.py $LIB_PATH/lib_pp_me.fasta $TEST_QUERY_ME
#python pys2/toSynTestLib.py $LIB_PATH/lib_pp_me.fasta $TEST_REF_ME
