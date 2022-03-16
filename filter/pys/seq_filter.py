#!/usr/bin/python
import sys
import os
import re
from .colorfulWriter import error_writer, warning_writer, log_writer
from .tools import classify, countLines, getTitle, getSeqDic, checkCOI, sortByLetter

# Filter all species
# @input
# dir_sps: a dir contains species files
# @return: None
def intra_sp_filter_all(dir_sps, dic_gR, ts_sp_pro, ts_sp_con):
    log_writer("***Intra-species filter!***\n...")
    ls_sp = os.listdir(dir_sps)
    temp_ref = dir_sps + 'temp_ref.fasta'
    os.mknod(temp_ref)
    temp_q = dir_sps + 'temp_q.fasta'
    os.mknod(temp_q)
    for species in ls_sp:
        if not "(" in species:
            intra_sp_filter(dic_gR, dir_sps, species, temp_ref, temp_q, ts_sp_pro, ts_sp_con)

# @input
# vf: "vsearch.COI"
# threshold: similarity threshold
# @return: line num that similarity higher than threshold
def vsearchSimiReader(vf, threshold):
    with open(vf) as f:
        items = f.read().splitlines()
    score_count = 0
    for i in range(len(items)):
        simi = float(items[i].split()[2])
        if simi >= float(threshold):
            score_count += 1
        else:
            return score_count
    return score_count

# get SCORE
# @input ...
# @return: a dic stored with {title:(seq, score, length)}
def circle_vsearch(dic, ref, temp, ts_sp_pro, ts_sp_con):
    dic_test = {}
    for title in dic:
        seq = dic.get(title)
        seq_num = int(countLines(ref)/2)
        with open(temp, "w+") as f:
            f.write(title+'\n'+seq+'\n')
        classify(ref, temp, ts_sp_con)
        num_con = countLines("result.COI")
        num_pro = vsearchSimiReader("result.COI", ts_sp_pro)
        score = num_pro*2 + num_con
        length = len(seq)
        dic_test[title] = (seq, score, length)
        rate = float(score/seq_num)
        if rate >= float(0.6*2+0.8) and length >= 600:
            return dic_test
    return dic_test

# get the seq with highest score
# @input
# dic_test: a dic stored with {title:(seq, score, length)}
# @return: a seq with highest score
def getBestScore(dic_test):
    tuple0 = ()
    for it in dic_test:
        tuple1 = dic_test.get(it)
        if tuple0 == ():
            tuple0 = tuple1
        elif tuple1[1] > tuple0[1]:
            tuple0 = tuple1
        elif tuple1[1] == tuple0[1] and tuple1[2] > tuple0[2]:
            tuple0 = tuple1
    return tuple0[0]

# intra-species filter
# @input
# sp_f: species fasta file
# @return
def intra_sp_filter(dic_gR, dir_sps, sp_f, temp_ref, temp_q, ts_sp_pro, ts_sp_con):
    sp_name = os.path.splitext(sp_f)[0]
    sp_title = getTitle(sp_name, dic_gR)
    sp_f_ab = dir_sps + sp_f
    if not os.path.getsize(sp_f_ab):
        os.remove(sp_f_ab)
    else:
        with open(sp_f_ab) as f:
            items = f.read().splitlines()
        dic_seqs = {}
        if len(items) == 2:
            sp_seq = items[1]
        else:
            for i in range(len(items)):
                if i % 2 == 0:
                    title = re.split("[ |]", items[i])[0]
                    seq = items[i+1]
                    dic_seqs[title] = seq
            dic_test = circle_vsearch(dic_seqs, sp_f_ab, temp_q, ts_sp_pro, ts_sp_con)
            sp_seq = getBestScore(dic_test)
        with open(temp_ref, 'a+') as f:
            f.write(sp_title+'\n'+sp_seq+'\n')
        os.remove(sp_f_ab)
    print("Intra-species filter of species "+sp_name+" finished!")

# inter-species filter
# @input
# @return
def inter_sp_filter(output_f, dic_abd, dir_sps, high_simi_dir, ts_sp_pro):
    temp_ref = dir_sps+'temp_ref.fasta'
    temp = dir_sps+'temp_q.fasta'
    log_writer("***Intra-species filter!***\n...")
    dic_seq = getSeqDic_sp(temp_ref)
    for ti in dic_seq:
        if dic_seq.get(ti)[1] == 1:
            title = ">"+ti
            seq = dic_seq.get(ti)[0]
            with open(temp, "w+") as f:
                f.write(title+'\n'+seq+'\n')
            classify(temp_ref, temp, ts_sp_pro)
            num_pro = countLines("result.COI")
            if num_pro > 1:
                list_titles = getHighSimiSeqs()
                dic_temp = {}
                list_genus = []
                abd_seq = ()
                for tt in list_titles:
                    genus = tt.split("__")[3]
                    species = tt.split("__")[4]
                    gs = genus + "_" + species
                    if genus not in list_genus:
                        list_genus.append(genus)
                    dic_seq.get(tt)[1] = 0
                    se = dic_seq.get(tt)[0]
                    dic_temp[tt] = se
                    abd = dic_abd.get(gs, 0)
                    if abd == 0:
                        warning_writer("species [ "+gs.replace("_"," ")+" ] has no sequence found!")
                    if not ("sp." in tt or "cf." in tt):
                        length = len(se) + 10000
                    else:
                        length = len(se)
                    if abd_seq == ():
                        abd_seq = (tt, se, abd, length)
                    elif abd > abd_seq[2]:
                        abd_seq = (tt, se, abd, length)
                    elif abd == abd_seq[2] and length > abd_seq[3]:
                        abd_seq = (tt, se, abd, length)
                with open(output_f, "a+") as f:
                    f.write(">"+abd_seq[0]+'\n'+abd_seq[1]+'\n')
                if not len(list_genus) == 1:
                    abd_title = abd_seq[0]
                    warning_writer("species [ "+abd_title+" ] might be other genus!")
                    high_simi_file = high_simi_dir+"high_simi_"+abd_title+'.fas'
                    with open(high_simi_file, "w+") as f:
                        for t in dic_temp:
                            f.write(">"+t+'\n'+dic_temp.get(t)+'\n')
            elif num_pro == 1:
                with open(output_f, "a+") as f:
                    f.write(title+'\n'+seq+'\n')
                dic_seq.get(ti)[1] = 0
            else:
                error_writer('There is some error with "result.COI"!')
    sortByLetter(output_f)

# collect high similarity seqs
# @input: None
# @return: a list with high similarity seqs
def getHighSimiSeqs():
    with open("result.COI") as f:
        items = f.read().splitlines()
    list_titles = []
    for item in items:
        title = item.split("\t")[1]
        list_titles.append(title)
    return list_titles


# @input
# inputf: a fasta file
# @return: a dic with {title: [seq, status]}
def getSeqDic_sp(inputf):
    with open(inputf) as f:
        items = f.read().splitlines()
    dic_seqs = {}
    for i in range(len(items)):
        if i % 2 == 0:
            title = items[i].replace(">", "", 1)
            seq = items[i+1]
            if title not in dic_seqs:
                dic_seqs[title] = [seq, 1]
    return dic_seqs

# @input
# @return
def getAbundance(sp_dist):
    dic_abundance = {}
    for item in os.listdir(sp_dist):
        if not item.startswith('temp_'):
            abundance = int(countLines(sp_dist + item)/2)
            sp_name = os.path.splitext(item)[0]
            if not sp_name in dic_abundance:
                dic_abundance[sp_name] = abundance
    return dic_abundance

