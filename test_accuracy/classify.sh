#!/usr/bin/bash
#Type "sh classify.sh -i INPUTFILE -o OUTPUTFILE -j METHOD -t $TREADS".
#"IS_UNCLASSIFY" is for some parameters that need not classification;
#TYPE "sh classify -h" to get more information.

#Temp
TEMP_DIR='temp'
RESULT_COI=$TEMP_DIR/result.COI

#Common
OUTDIR='dist'
RESULT=$OUTDIR/assign_per_query.tsv
log='log/log'
THREADS=8

#0
#Threshold similarity that whether will be used in main table.
THRESHOLD='95'

#Switch
IS_UNCLASSIFY=0
IS_UNIQUE=0
ALIGN=0
JPLACE_MADE_METHOD=1
#IS_ALIGNED=0
IS_SPEED_TEST=0
IS_TEST=0

#Path of input/outpot
OUTPUT='test_accuracy/result.csv'
#LOAD_PATH='test_accuracy/test_lib/Collembola_16S/5'
LOAD_PATH="lib/Collembola_COI"
#LIB_1 is similarity-based, LIB_2 is pp_based.
LIB_1=$LOAD_PATH/lib.fasta
LIB_2=$LOAD_PATH/lib_pp.fasta
LIB_ME=$LOAD_PATH/lib_pp_me.fasta
LIB_3=$LOAD_PATH/hs-blastn/lib.fasta
TREE=$LOAD_PATH/lib_pp.nwk
TREE_ME=$LOAD_PATH/lib_pp_me.nwk
LABEL=$LOAD_PATH/name.label
UNION=$LOAD_PATH/rappas/DB_session_k8_o1.5.union

#LIB_1=$LOAD_PATH/test_vref.fasta
#LIB_2=$LOAD_PATH/test_ref.fasta
#TREE=$LOAD_PATH/test_ref.nwk
#LABEL=$LOAD_PATH/test.label
#UNION=$LOAD_PATH/rappas/DB_session_k8_o1.5.union


##########################################################
###----------------------Functions------------------------

function clean(){
    if [ -s $1 ]; then
	rm -rf $1
    fi
}

function exit_with_clean() {
    clean "$RESULT_COI"
    clean "$cp_inf"
    clean "$v_inf"
    clean "$PER_TEMP_FASTA"
    clean "$PER_TEMP_CSV"

    echo "Run with -h for more information."
    exit 1
}

function echo_and_log(){
    echo -e $1
    echo -e $1 >> $log
}


##########################################################
###-----------------------Options-------------------------

while getopts ":o:i:g:j:l:s:t:EUThv" opt
do
    case $opt in
	o)
	OUTPUT=$OPTARG;;
	i)
	inp=$OPTARG
	inf=`echo $inp | rev | cut -d '/' -f 1 | rev`
	cp_inf_n=copy_$inf
	cp_inf=$TEMP_DIR/$cp_inf_n
	v_inf_n=v_$inf
	v_inf=$TEMP_DIR/$v_inf_n
	;;
	j)
	if [ $OPTARG -eq 1 ]; then
	  JPLACE_MADE_METHOD=1
	elif [ $OPTARG -eq 2 ]; then
	  JPLACE_MADE_METHOD=2
	elif [ $OPTARG -eq 3 ]; then
	  JPLACE_MADE_METHOD=3
	elif [ $OPTARG -eq 5 ]; then
	  JPLACE_MADE_METHOD=5
	elif [ $OPTARG -eq 6 ]; then
	  JPLACE_MADE_METHOD=6
	else
	  echo "Warning: invalid input of '-j', it will be set in default(value='1')!"
	fi
	;;
	l)
	LOAD_PATH=$OPTARG
	LIB_1=$LOAD_PATH/lib.fasta
	LIB_2=$LOAD_PATH/lib_pp.fasta
	LIB_ME=$LOAD_PATH/lib_pp_me.fasta
	LIB_3=$LOAD_PATH/hs-blastn/lib.fasta
	TREE=$LOAD_PATH/lib_pp.nwk
	TREE_ME=$LOAD_PATH/lib_pp_me.nwk
	LABEL=$LOAD_PATH/name.label
	UNION=$LOAD_PATH/rappas/DB_session_k8_o1.5.union
	;;
	s)
	THRESHOLD=$OPTARG;;
	t)
	THREADS=$OPTARG;;
	E)
	IS_TEST=1;;
	U)
	IS_UNIQUE=1;;
	T)
	IS_SPEED_TEST=1;;
	h)
	echo """Usage: sh classify.sh [OPTIONS] -i query_file(required)

Options:
  -i input_file:	A fasta file is needed.
  -o output_file:	'.csv' file is recommanded.
  -U unique		When '-U' is on, for each of the sequences classified with pp methods, only the result with higest LWR values will be remained.

  -T time_used		Show time used.
  -s threshold		When 'jplace made'==0, sequences with similarity > threshold and have same genus information as epa-ng will be added species information in the result file.

  -j jplace made:	Choose the method to produce 'jplace' format file.
			1: epa-ng
			2: rappas
			3: apples
			4: pplacer(waiting for it!)
			5: vsearch
			6: hs-blastn
			0: epa-ng with species level that from vsearch (>threshold)
  -l load_path		A path contains lib files.
  -E is_test		Load test path.
  -t threads		default:8
  -h help
  -v version
"""
	exit 1
	;;
	v)
	cat pre/version/version_now.txt
	exit 1;;
	?)
        echo "error: unexpected input"
        exit_with_clean;;
    esac
done

##########################################################
###------------------------Error--------------------------

if ! [ -n "$inp" ] && [ $IS_UNCLASSIFY -eq 0 ]; then
  echo "Error: query_file, as a fasta file, is needed."
  exit_with_clean
fi

if `echo $THRESHOLD | grep -q '[^0-9]'` || [ $THRESHOLD -gt 100 ]; then
  echo "Error: the threshold of species level should be set at 0-100. And the thresholds shouldbe set in 'int'"
  exit_with_clean
fi

#if `echo $ID_SP$ID_GENUS | grep -q '[^0-9]'` || [ $ID_SP -le $ID_GENUS ]; then
#  echo "Error: the threshold of species level should be higer than genus level when using vsearch. And the thresholds should be set in 'int'"
#  exit_with_clean
#fi

#if [ $ID_GENUS -ge 100 ] || [ $ID_GENUS -lt 70 ] || [ $ID_SP -gt 100 ] || [ $ID_SP -lt 80 ]; then
#  echo 'Error: "-s 80-100(d:95); -g 70-99(d:90)."'
#  exit_with_clean
#fi

##########################################################
##########################################################
###--------------------Classification---------------------

seqkit seq -w 0 $inp | sed "s/ /_/g" | sed "s/;/,/g" | sed "s/__/_/g" > $cp_inf
IS_DOUBLE_UNDERLINE=`grep "__" $cp_inf`
IS_SEMICOLON=`grep ";" $cp_inf`

#if ! [ -z "$IS_DOUBLE_UNDERLINE" ]; then
#  echo 'Error: unexpected input of the query fasta file(DOUBLE_UNDERLINE)'
#  exit_with_clean
#fi

if ! [ -z "$IS_SEMICOLON" ]; then
  echo 'Error: unexpected input of the query fasta file(SEMICOLON)'
  exit_with_clean
fi

LINE_NUM=`awk 'END{print NR}' $cp_inf`
((SEQ_NUM=$LINE_NUM/2))

#
if [ $IS_TEST -eq 1 ]; then
  LIB_1=$LOAD_PATH/test_vref.fasta
  LIB_2=$LOAD_PATH/test_ref.fasta
  LIB_ME=$LOAD_PATH/test_ref_me.fasta
  LIB_3=$LOAD_PATH/hs-blastn/test_vref.fasta
  TREE=$LOAD_PATH/test_ref.nwk
  TREE_ME=$LOAD_PATH/test_ref_me.nwk
  LABEL=$LOAD_PATH/test.label
  UNION=$LOAD_PATH/rappas/DB_session_k8_o1.5.union
fi

#Treat the query seqs with same titles.
python -c "from pys import queryTreater; queryTreater.sameTitleTreater('$cp_inf')"

echo "NO.;title;Kingdom;Phylum;Class;Order;Family;Genus;species;Similarity;aLWR" > $OUTPUT
>$log
echo_and_log "***\n...\nOpen the file [ $inf ] now...\n"

if [ $IS_SPEED_TEST -eq 1 ]; then
	START_TIME=$(date +%s.%N | cut -b 1-14)
fi

################################################################
################################################################
	  ###Phylogenetic placement based result/Gappa result###

################################################################
	  #################jplace made  methods#################

rm -rf $OUTDIR/*

#Allignment
#if [ $ALIGN -eq 1 ] && [ $JPLACE_MADE_METHOD -lt 5 ]; then
#	LEN_LIB=`python -c "from pys import alignment; print(alignment.f2p('$LIB_2', '$TEMP_DIR/lib_pp.phylip'))"`
#	papara -j $THREADS -t $TREE -s $TEMP_DIR/lib_pp.phylip -q $cp_inf
#	python -c "from pys import alignment; alignment.seqSep($LEN_LIB//2)"
#	LIB_2=$TEMP_DIR/lib_pp.fas
#	cp_inf=$TEMP_DIR/query.fas
#fi

################################################################
          #######################do epa-ng######################

if [ $JPLACE_MADE_METHOD -eq 1 ]; then
	epa-ng --ref-msa $LIB_2 --tree $TREE --query $cp_inf --model 'GTR+G' --outdir $OUTDIR --threads $THREADS

	JPLACE=$OUTDIR/epa_result.jplace

################################################################
          #######################do rappas######################

elif [ $JPLACE_MADE_METHOD -eq 2 ]; then
	rappas -p p -d $UNION -q $cp_inf -w $OUTDIR --threads $THREADS

	JPLACE=$OUTDIR/placements_$cp_inf_n.jplace

################################################################
          #######################do apples######################

elif [ $JPLACE_MADE_METHOD -eq 3 ]; then
	JPLACE=$OUTDIR/apples.jplace
	run_apples.py -s $LIB_2 -q $cp_inf -t $TREE_ME -o $JPLACE -T $THREADS
fi

################################################################
          ########################do gappa######################

if [ $JPLACE_MADE_METHOD -lt 5 ]; then
    gappa examine assign --jplace-path $JPLACE --taxon-file $LABEL --out-dir $OUTDIR --per-query-results --allow-file-overwriting --threads $THREADS --file-prefix assign_

    #cp $RESULT $OUTDIR/cp.tsv

#To make scv result file.
#The result can't touch specific level will be regarded as null.
    python -c "from pys import resultShower; resultShower.gappaShower('$cp_inf','$RESULT','$OUTPUT', '$log')"

#Unique result shower for every QS.
    if [ $IS_UNIQUE -eq 1 ]; then
        python -c "from pys import resultShower; resultShower.uniqShower('$OUTPUT')"
    fi

#    for ((i=1;i<=$SEQ_NUM;i++))
#    do
#	((k=$i*2))
#	((j=$k-1))
#	sed -n "$j , $k p" $cp_inf > $PER_TEMP_FASTA
#	TITLE=`sed -n "$j p" $cp_inf | sed "s/>//"`
#	grep $TITLE $RESULT > $PER_TEMP_CSV

#	LINE_RESULT=`awk 'END{print NR}' $PER_TEMP_CSV`
#	if ! [ -s $PER_TEMP_CSV ] || [ $LINE_RESULT -lt 5 ]; then
#	    echo "$i;$TITLE;NoResult;Failed assigning to family level" >> $OUTPUT
#	elif [ $LINE_RESULT -eq 5 ]; then
#	    OUT_LINE=`sed -n "5p" $PER_TEMP_CSV`
#	    echo $OUT_LINE | sed "s/;/ /g" | awk '{print "'$i';'$TITLE';"$6";"$7";"$8";"$9";"$10";null;null;;"$2}' >> $OUTPUT
#	elif [ -z `echo $(sed -n "6p" $PER_TEMP_CSV | sed "s/;/ /g") | cut -d " " -f 11` ]; then
#	    for ((j=5;j<=$LINE_RESULT;j++))
#	    do
#		OUT_LINE=`sed -n "$j p" $PER_TEMP_CSV`
#		STRS=`echo $OUT_LINE | sed "s/;/ /g"`
#		if ! [ -z `echo $STRS | cut -d " " -f 10` ]; then
#		    echo $STRS | awk '{print "'$i';'$TITLE';"$6";"$7";"$8";"$9";"$10";null;null;;"$2}' >> $OUTPUT
#		fi
#	    done
#	else
#	    for ((j=6;j<=$LINE_RESULT;j++))
#	    do
#		OUT_LINE=`sed -n "$j p" $PER_TEMP_CSV`
#		STRS=`echo $OUT_LINE | sed "s/;/ /g"`
#		if ! [ -z `echo $STRS | cut -d " " -f 11` ]; then
#		    echo $STRS | awk '{print "'$i';'$TITLE';"$6";"$7";"$8";"$9";"$10";"$11";null;;"$2}' >> $OUTPUT
#		fi
#	    done
#	fi
#	echo_and_log "...\n[ $TITLE ] is successfully finished classifing!"
#    done
fi


################################################################
################################################################
          ###############Similarity based result################

################################################################
          ####################do vsearch########################

#if [ $JPLACE_MADE_METHOD -ge 5 ] || [ $JPLACE_MADE_METHOD -eq 0 ]; then
if [ $JPLACE_MADE_METHOD -eq 5 ]; then
    sed "s/-//g" $cp_inf > $v_inf
    vsearch --usearch_global $v_inf --db $LIB_1 --blast6out - --maxaccepts 1 --maxrejects 0 --id 0.1 --threads $THREADS > $RESULT_COI

    python -c "from pys import resultShower; resultShower.vsearchShower('$v_inf','$RESULT_COI','$OUTPUT', '$log')"

#    for ((i=1;i<=$SEQ_NUM;i++))
#    do
#	((k=$i*2))
#	((j=$k-1))
#	sed -n "$j , $k p" $v_inf > $PER_TEMP_FASTA
#	TITLE=`sed -n "$j p" $v_inf | sed "s/>//"`
#	grep $TITLE $RESULT_COI > $PER_TEMP_CSV

#	if ! [ -s $PER_TEMP_CSV ]; then
#	    echo "$i;$TITLE;NoResult;Failed to match" >> $OUTPUT
#	else
#	    cat $PER_TEMP_CSV | sed "s/__/ /g" | awk '{print "'$i';'$TITLE';Eukaryota;Animalia;"$2";"$3";"$4";"$5";"$6";"$7";"}' >> $OUTPUT
#	fi
#	echo_and_log "...\n[ $TITLE ] is successfully finished classifing!"
#    done
fi

################################################################
          ####################do hs-blastn######################
if [ $JPLACE_MADE_METHOD -eq 6 ]; then
    sed "s/-//g" $cp_inf > $v_inf
    hs-blastn align -db $LIB_3 -query $v_inf -out $RESULT_COI -outfmt 7 -max_target_seqs 1 -num_threads $THREADS
    python -c "from pys import resultShower; resultShower.blastnShower('$v_inf','$RESULT_COI','$OUTPUT', '$log')"
fi


##########################################################
###--------------------post processing--------------------


echo_and_log "\n------***End***------\n"

#Show time used.
if [ $IS_SPEED_TEST -eq 1 ]; then
        END_TIME=$(date +%s.%N | cut -b 1-14)
	TIME_USED=`echo "$END_TIME- $START_TIME"|bc`
	#let TIME_USED=END_TIME-START_TIME
	echo "Time used: $TIME_USED s"
fi

#clean "$RESULT_COI"
#clean "$cp_inf"
#clean "$v_inf"
if [ "$(ls -A $TEMP_DIR)" ]; then
    rm temp/*
fi
#if [ $IS_ALIGNED -eq 1 ] && [ $JPLACE_MADE_METHOD -lt 5 ]; then
#    rm papara_*
#fi
