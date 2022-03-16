#!/usr/bin/bash
#Type "sh classify.sh -i INPUTFILE -o OUTPUTFILE -j METHOD -p/-l DATABASE -t $THREADS".
#TYPE "sh classify -h" to get more information.

#pwd
WORK_PATH=$(dirname $0)"/"
#Temp
TEMP_DIR=$WORK_PATH'temp'
RESULT_COI=$TEMP_DIR/result.COI

#Common
OUTDIR=$WORK_PATH'dist'
RESULT=$OUTDIR/assign_per_query.tsv
log=$WORK_PATH'log/log'
THREADS=1

#0
#For similarity-based methods.
MAXACCEPTS=1
THRESHOLD=0

#For pp-based methods.
IS_UNIQUE=0
IS_ALIGNED=0

#Switch
IS_UNCLASSIFY=0
JPLACE_MADE_METHOD=1
IS_DESIGNATED=0
IS_SPEED_TEST=0

#Path of input/outpot
OUTPUT='result.csv'
LOAD_PATH=$WORK_PATH"lib/Collembola_COI"
#LIB_1 is similarity-based, LIB_2 is pp_based.
LIB_1=$LOAD_PATH/lib.fasta
LIB_2=$LOAD_PATH/lib_pp.fasta
TREE=$LOAD_PATH/lib_pp.nwk
TREE_ME=$LOAD_PATH/lib_pp_me.nwk
LABEL=$LOAD_PATH/name.label
UNION=$LOAD_PATH/rappas/DB_session_k8_o1.5.union
LIB_HS=$LOAD_PATH/hs-blastn/lib.fasta


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

function echo_and_log_warning(){
    echo_and_log "\033[33mWarning: $1\033[0m"
}

function echo_and_log_error(){
    echo_and_log "\033[31mError: $1\033[0m"
    exit_with_clean
}

>$log

##########################################################
###-----------------------Options-------------------------

while getopts ":o:i:g:j:p:l:r:f:n:m:a:u:s:t:x:UTAhv" opt
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
	  echo_and_log_warning "invalid input of '-j', it will be set in default(epa-ng)!"
	  #echo -e "\033[33mWarning: invalid input of '-j', it will be set in default(epa-ng)!\033[0m"
	fi
	ISSET_METHOD=1
	;;
	p)
	if [ $IS_DESIGNATED -eq 1 ]; then
          echo_and_log_error "parameter conflicts exist ('-p')!"
        fi
	if [ $OPTARG -eq 11 ]; then
	  LOAD_PATH=lib/Collembola_COI
	elif [ $OPTARG -eq 12 ]; then
	  LOAD_PATH=lib/Collembola_16S
	elif [ $OPTARG -eq 13 ]; then
	  LOAD_PATH=lib/Collembola_18S
	elif [ $OPTARG -eq 21 ]; then
	  LOAD_PATH=lib/Acari_COI
	elif [ $OPTARG -eq 22 ]; then
	  LOAD_PATH=lib/Acari_16S
	elif [ $OPTARG -eq 23 ]; then
	  LOAD_PATH=lib/Acari_18S
	elif [ $OPTARG -eq 31 ]; then
	  LOAD_PATH=lib/Clitellata_COI
	elif [ $OPTARG -eq 32 ]; then
	  LOAD_PATH=lib/Clitellata_16S
	elif [ $OPTARG -eq 33 ]; then
	  LOAD_PATH=lib/Clitellata_18S
	elif [ $OPTARG -eq 41 ]; then
	  LOAD_PATH=lib/Chromadorea_COI
	elif [ $OPTARG -eq 42 ]; then
	  LOAD_PATH=lib/Chromadorea_16S
	elif [ $OPTARG -eq 43 ]; then
	  LOAD_PATH=lib/Chromadorea_18S
	else
	  echo_and_log_warning "invalid input of '-p', it will be set in default(Collembola_COI)!"
	fi
	LIB_1=$LOAD_PATH/lib.fasta
	LIB_2=$LOAD_PATH/lib_pp.fasta
	TREE=$LOAD_PATH/lib_pp.nwk
	TREE_ME=$LOAD_PATH/lib_pp_me.nwk
	LABEL=$LOAD_PATH/name.label
	UNION=$LOAD_PATH/rappas/DB_session_k8_o1.5.union
	LIB_HS=$LOAD_PATH/hs-blastn/lib.fasta
	ISSET_LIB=1
	;;
	l)
	if [ $IS_DESIGNATED -eq 1 ]; then
          echo_and_log_error "parameter conflicts exist ('-l')!"
	fi
	LOAD_PATH=$OPTARG
	LIB_1=$LOAD_PATH/lib.fasta
	LIB_2=$LOAD_PATH/lib_pp.fasta
	TREE=$LOAD_PATH/lib_pp.nwk
	TREE_ME=$LOAD_PATH/lib_pp_me.nwk
	LABEL=$LOAD_PATH/name.label
	UNION=$LOAD_PATH/rappas/DB_session_k8_o1.5.union
	LIB_HS=$LOAD_PATH/hs-blastn/lib.fasta
	;;
	r)
	LIB_1=$OPTARG
	IS_DESIGNATED=1
	;;
	f)
	LIB_2=$OPTARG
	IS_DESIGNATED=1
	;;
	n)
	TREE=$OPTARG
	IS_DESIGNATED=1
	;;
	m)
	TREE_ME=$OPTARG
	IS_DESIGNATED=1
	;;
	a)
	LABEL=$OPTARG
	IS_DESIGNATED=1
	;;
	u)
	UNION=$OPTARG
	IS_DESIGNATED=1
	;;
	b)
	LIB_HS=$OPTARG
	IS_DESIGNATED=1
	;;
	s)
	THRESHOLD=$OPTARG
	ISSET_THRESHOLD=1;;
	x)
	MAXACCEPTS=$OPTARG
	ISSET_MAXACCEPTS=1
	;;
	t)
	THREADS=$OPTARG;;
	U)
	IS_UNIQUE=1;;
        T)
        IS_SPEED_TEST=1;;
	A)
	IS_ALIGNED=1
	if [ $(which papara) ]; then
	  echo "papara ...... OK"
	  EXE_PAPARA=$(which papara)
	  DIR_PAPARA=${EXE_PAPARA%/*}
	else
	  until [ -x $DIR_PAPARA/papara ]
	    do
	      read -p "papara is not found. Please input its installation directory:      " DIR_PAPARA
	    done
	  echo "papara ...... OK"
	fi
	;;
	h)
	echo """Usage: sh classify.sh [OPTIONS] -i query_file(required)

Options:
  -i input_file:	A fasta file is needed.
  -o output_file:	'.csv' format is recommanded ('.xlsx' format is also supported).

  -j assignment method	Choose the method to accomplish taxonomic assignment (default: epa-ng):
			1: epa-ng
			2: rappas
			3: apples
			5: vsearch
			6: hs-blastn

  -p path		A local path contains lib files (default: Colembola/COI).
			11: Collembola/COI
			12: Collembola/16S
			13: Collembola/18S
			21: Acari/COI
			22: Acari/16S
			23: Acari/18S
			31: Clitellata/COI
			32: Clitellata/16S
			33: Clitellata/18S
			41: Chromadorea/COI
			42: Chromadorea/16S
			43: Chromadorea/18S
  -l load_path		A path contains lib files.
			Lib files should be named as:
			lib.fasta: described as -r
			lib_pp.fasta: described as -f
			lib_pp.nwk: described as -n
			lib_pp_me.nwk: described as -m
			name.label: described as -a
			DB_session_k8_o1.5.union: described as -u

  -r ref1		A reference fasta file for similarity-based methods
  -f ref2		A reference fasta file for phylogenetic-placement-based methods
  -n tree file1		A reference tree file for phylogenetic-placement-based methods
  -m tree file2		A reference tree file for apples
  -a name list		A name list file for phylogenetic-placement-based methods
  -u union file		A union file for rappas
  -b blastn lib file	A lib file used in hs-blastn

  -T time_used		Show time used ([switch]).
  -U unique		When '-U' is on, for each of the sequences classified with gappa, only the result with higest LWR values will be remained ([switch]; for phylogenetic-placement-based methods).
  -A alignment		Alignment for epa-ng and apples ([switch]; for phylogenetic-placement-based methods).

  -s threshold		The similarity threshold for result showing (float, 0-1, default: 0; for similarity-based methods).
  -x maxaccepts		The number of max matches showing for each query sequence (int, default:1; for similarity-based methods).

  -t threads		default:1
  -h help
  -v version
"""
	exit 1
	;;
	v)
	cat $WORK_PATH'version/version_now.txt'
	exit 1;;
	?)
        echo_and_log_error "unexpected parameters!";;
    esac
done

##########################################################
###------------------------Error--------------------------

if ! [ -n "$inp" ] && [ $IS_UNCLASSIFY -eq 0 ]; then
  echo_and_log_error "an input file including query sequences is required!"
fi

#python -c "from ppys import checker; print checker.checkThreshold('$log','$THRESHOLD')"

#if `echo $ID_SP$ID_GENUS | grep -q '[^0-9]'` || [ $ID_SP -le $ID_GENUS ]; then
#  echo "Error: the threshold of species level should be higer than genus level when using vsearch. And the thresholds should be set in 'int'"
#  exit_with_clean
#fi

#if [ $ID_GENUS -ge 100 ] || [ $ID_GENUS -lt 70 ] || [ $ID_SP -gt 100 ] || [ $ID_SP -lt 80 ]; then
#  echo 'Error: "-s 80-100(d:95); -g 70-99(d:90)."'
#  exit_with_clean
#fi

##########################################################
###------------------------Warning------------------------

#Warning for default 
if [ ! -n "$ISSET_METHOD" ]; then
  echo_and_log_warning "the assignment method (option '-j') was not set and it was automatically set to the default (epa-ng)!"
fi
if [ ! -n "$ISSET_LIB" ]; then
  echo_and_log_warning "the reference database (option '-p' or '-l') was not set and it was automatically set to the default (Collembola/COI)!"
fi

#warning for the options merely applied with similarity-based methods
if [ $JPLACE_MADE_METHOD -lt 5 ]; then
  if [ -n "$ISSET_MAXACCEPTS" ]; then
    echo_and_log_warning "the option '-x' is only applied in similarity-based methods!"
  fi
  if [ -n "$ISSET_THRESHOLD" ]; then
    echo_and_log_warning "the option '-s' is only applied in similarity-based methods!"
  fi
fi

#warning for the options merely applied with pp-based methods
if [ $JPLACE_MADE_METHOD -ge 5 ]; then
  python -c "from ppys import checker; checker.checkThreshold('$log','$THRESHOLD')"
  if [ $IS_UNIQUE -eq 1 ]; then
    echo_and_log_warning "the option '-U' is only applied in phylogenetic-placement-based methods!"
  fi
  if [ $IS_ALIGNED -eq 1 ]; then
    echo_and_log_warning "the option '-A' is only applied in phylogenetic-placement-based methods!"
  fi
fi

##########################################################
##########################################################
###--------------------Classification---------------------
#Time
CRTIME=$(date)
echo_and_log "$CRTIME"

#seqkit seq -w 0 $inp | sed "s/ /_/g" | sed "s/;/,/g" | sed "s/__/_/g" > $cp_inf
python -c "from ppys import queryTreater; queryTreater.oneLineQSTreater('$inp','$cp_inf')"
if [ $? -eq 1 ]; then
  echo_and_log_error  'unexpected input of the query fasta file!'
fi
#sed -i -e  "s/ /_/g" -e "s/;/,/g" -e "s/__/_/g" $cp_inf
IS_DOUBLE_UNDERLINE=`grep "__" $cp_inf`
IS_SEMICOLON=`grep ";" $cp_inf`

#if ! [ -z "$IS_DOUBLE_UNDERLINE" ]; then
#  echo 'Error: unexpected input of the query fasta file(DOUBLE_UNDERLINE)'
#  exit_with_clean
#fi

if ! [ -z "$IS_SEMICOLON" ]; then
  echo_and_log_error  'unexpected input of the query fasta file(SEMICOLON)!'
fi

LINE_NUM=`awk 'END{print NR}' $cp_inf`
((SEQ_NUM=$LINE_NUM/2))

#Treat the query seqs with same titles.
python -c "from ppys import queryTreater; queryTreater.sameTitleTreater('$cp_inf')"

echo "NO.;title;Kingdom;Phylum;Class;Order;Family;Genus;species;Similarity;aLWR" > $OUTPUT
echo_and_log "***\n...\nOpen the file [ $inf ] now...\n"

#Show time used.
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
if [ $IS_ALIGNED -eq 1 ] && [ $JPLACE_MADE_METHOD -lt 5 ]; then
	LEN_LIB=`python -c "from ppys import alignment; print(alignment.f2p('$LIB_2', '$TEMP_DIR/lib_pp.phylip'))"`
	$DIR_PAPARA/papara -j $THREADS -t $TREE -s $TEMP_DIR/lib_pp.phylip -q $cp_inf
	python -c "from ppys import alignment; alignment.seqSep('$TEMP_DIR',$LEN_LIB//2)"
	LIB_2=$TEMP_DIR/lib_pp.fas
	cp_inf=$TEMP_DIR/query.fas
fi

################################################################
          #######################do epa-ng######################

if [ $JPLACE_MADE_METHOD -eq 1 ]; then
	if [ $(which epa-ng) ]; then
          echo "epa-ng ...... OK"
          EXE_EPANG=$(which epa-ng)
          DIR_EPANG=${EXE_EPANG%/*}
        else
          until [ -x $DIR_EPANG/epa-ng ]
            do
              read -p "epa-ng is not found. Please input its installation directory:      " DIR_EPANG
            done
          echo "epa-ng ...... OK"
        fi
	$DIR_EPANG/epa-ng --ref-msa $LIB_2 --tree $TREE --query $cp_inf --threads $THREADS --model 'GTR+G' --outdir $OUTDIR

	JPLACE=$OUTDIR/epa_result.jplace

################################################################
          #######################do rappas######################

elif [ $JPLACE_MADE_METHOD -eq 2 ]; then
	if [ $(which rappas) ]; then
          echo "rappas ...... OK"
          EXE_RAPPAS=$(which rappas)
          DIR_RAPPAS=${EXE_RAPPAS%/*}
        else
          until [ -x $DIR_RAPPAS/rappas ]
            do
              read -p "rappas is not found. Please input its installation directory:      " DIR_RAPPAS
            done
          echo "rappas ...... OK"
        fi
	$DIR_RAPPAS/rappas -p p -d $UNION -q $cp_inf -w $OUTDIR --threads $THREADS

	JPLACE=$OUTDIR/placements_$cp_inf_n.jplace

################################################################
          #######################do apples######################

elif [ $JPLACE_MADE_METHOD -eq 3 ]; then
	if [ $(which run_apples.py) ]; then
          echo "run_apples.py ...... OK"
          EXE_APPLES=$(which run_apples.py)
          DIR_APPLES=${EXE_APPLES%/*}
        else
          until [ -x $DIR_APPLES/run_apples.py ]
            do
              read -p "run_apples.py is not found. Please input its installation directory:      " DIR_APPLES
            done
          echo "run_apples.py ...... OK"
        fi
	JPLACE=$OUTDIR/apples.jplace
	$DIR_APPLES/run_apples.py -s $LIB_2 -q $cp_inf -t $TREE_ME -o $JPLACE -T $THREADS
fi

################################################################
          ########################do gappa######################

if [ $JPLACE_MADE_METHOD -lt 5 ]; then
    if [ $(which gappa) ]; then
      echo "gappa ...... OK"
      EXE_GAPPA=$(which gappa)
      DIR_GAPPA=${EXE_GAPPA%/*}
    else
      until [ -x $DIR_GAPPA/gappa ]
        do
          read -p "gappa is not found. Please input its installation directory:      " DIR_GAPPA
        done
      echo "gappa ...... OK"
    fi
    $DIR_GAPPA/gappa examine assign --jplace-path $JPLACE --taxon-file $LABEL --out-dir $OUTDIR --per-query-results --allow-file-overwriting --threads $THREADS --file-prefix assign_

    #cp $RESULT $OUTDIR/cp.tsv

#To make scv result file.
#The result can't touch specific level will be regarded as null.
    python -c "from ppys import resultShower; resultShower.gappaShower('$cp_inf','$RESULT','$OUTPUT', '$log')"

#Unique result shower for every QS.
    if [ $IS_UNIQUE -eq 1 ]; then
        python -c "from ppys import resultShower; resultShower.uniqShower('$OUTPUT')"
    fi

fi


################################################################
################################################################
          ###############Similarity based result################

################################################################
          ####################do vsearch########################

if [ $JPLACE_MADE_METHOD -eq 5 ] || [ $JPLACE_MADE_METHOD -eq 0 ]; then
    if [ $(which vsearch) ]; then
          echo "vsearch ...... OK"
          EXE_VSEARCH=$(which vsearch)
          DIR_VSEARCH=${EXE_VSEARCH%/*}
    else
          until [ -x $DIR_VSEARCH/vsearch ]
            do
              read -p "vsearch is not found. Please input its installation directory:      " DIR_VSEARCH
            done
          echo "vsearch ...... OK"
    fi
    sed "s/-//g" $cp_inf > $v_inf
    $DIR_VSEARCH/vsearch --usearch_global $v_inf --db $LIB_1 --blast6out - --maxaccepts $MAXACCEPTS --maxrejects 0 --id $THRESHOLD --threads $THREADS > $RESULT_COI

    python -c "from ppys import resultShower; resultShower.vsearchShower('$v_inf','$RESULT_COI','$OUTPUT', '$log')"

fi

################################################################
          ####################do hs-blastn######################
if [ $JPLACE_MADE_METHOD -eq 6 ]; then
    if [ $(which hs-blastn) ]; then
          echo "hs-blastn ...... OK"
          EXE_HSBLASTN=$(which hs-blastn)
          DIR_HSBLASTN=${EXE_HSBLASTN%/*}
    else
          until [ -x $DIR_HSBLASTN/hs-blastn ]
            do
              read -p "hs-blastn is not found. Please input its installation directory:      " DIR_HSBLASTN
            done
          echo "hs-blastn ...... OK"
    fi
    sed "s/-//g" $cp_inf > $v_inf
    PERC_ID=$(echo "$THRESHOLD * 100"|bc)
    $DIR_HSBLASTN/hs-blastn align -db $LIB_HS -query $v_inf -out $RESULT_COI -outfmt 7 -max_target_seqs $MAXACCEPTS -num_threads $THREADS -perc_identity $PERC_ID
    python -c "from ppys import resultShower; resultShower.blastnShower('$v_inf','$RESULT_COI','$OUTPUT', '$log')"
fi


##########################################################
###--------------------post processing--------------------


echo_and_log "\n------***End***------\n"

#Output for excel.
python -c "from ppys import resultShower; resultShower.excelShower('$OUTPUT')"

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
    rm $TEMP_DIR/*
fi
if [ $IS_ALIGNED -eq 1 ] && [ $JPLACE_MADE_METHOD -lt 5 ]; then
    rm papara_*
fi
