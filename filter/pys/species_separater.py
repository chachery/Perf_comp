#!/usr/bin/python
# Type 'taxonkit list --show-rank --show-name --indent " " --ids $TXID' to get taxon file. 
import sys
import os
import re
from .colorfulWriter import error_writer, warning_writer, log_writer
from .tools import ck, typeSearch, classify_hs, rev_comp

# @input
# taxonf: taxon file prodeced with taxonkit
# @return: list format of taxon file
def checkClazz(taxonf):
    with open(taxonf) as f:
        alls = f.read()
    if not ('[order]' in alls and '[class]' in alls):
        warning_writer('There is no "[class]" line or "[order]" line in the taxon file.\nEg. Add "100001 [class] $CLASSNAME" at first line.')
    return alls.splitlines()

# @input
# list_taxon: a list consists of every line of taxon file
# @return: 1: a dic stored with {genus:(family,order,clazz)}
#        & 2: a list stores species names from BOLD
def genusRegister(list_taxon, BOLDf):
    clazz = order = family = genus = ""
    #store with {genus:(family,order,clazz)}
    dic_gR={}
    for i in range(len(list_taxon)):
        item = list_taxon[i]
        if not "[" in item:
            continue
        its = re.split('[\[\]]', item)
        rank = its[1]
        name = its[2].strip()
        if rank == "genus":
            if order == "" or clazz == "":
                error_writer('There is no "[class]" line or "[order]" line in the taxon file.\nEg. Add "100001 [class] $CLASSNAME" at first line.')
            if name not in dic_gR:
                dic_gR[name] = (family,order,clazz)
            else:
                warning_writer("genus ["+genus+"] has been repeated")
        elif rank == "family":
            family = name
            if order == "":
                order = input("Please input order name: ")
            if clazz == "":
                clazz = input("Please input class name: ")
        elif rank == "order":
            order = name
        elif rank == "class":
            clazz = name
    if not BOLDf == "null":
        tuple1 = BOLDTreater(BOLDf, dic_gR, clazz, order)
        return tuple1
    return (dic_gR,[])

# @input
# BOLDf: BOLD file
# dic_gR:a dic stored with {genus:(family,order,clazz)}
# @return: 1: a dic stored with {genus:(family,order,clazz)}(add BOLD genura)
#        & 2: a species list of BOLD file
def BOLDTreater(BOLDf, dic_gR, clazz, order):
    clazz = clazz
    order = order
    with open(BOLDf) as f:
        items = f.read().splitlines()
    list_BOLD_sp=[]
    for i in range(len(items)):
        item = items[i]
        if item.strip() == "" or not item:
            continue
        its = item.split("\t")
        rank = its[0]
        name = its[1].strip()
        level_name = name.split()[0]
        if rank == " " or rank == "[genus]":
            genus = level_name
            if not genus.endswith("GEN"):
                if not genus in dic_gR:
                    dic_gR[genus] = (family,order,clazz)
                if not name.endswith("sp.") and name not in list_BOLD_sp:
                    list_BOLD_sp.append(name)
        elif rank == "[family]":
            family = level_name
        elif rank == "[order]":
            order = name
        elif rank == "[class]":
            if clazz != name:
                clazz = name
                warning_writer('Class name has been changed!')
    return (dic_gR, list_BOLD_sp)


# @input
# list_taxon: a list consists of every line of taxon file
# a dic stored with {genus:(family,order,clazz)}
# @return: a list stores species names
def speciesListMaker(list_taxon, tuple1):
    dic_gR = tuple1[0]
    list_sp = tuple1[1]
    for i in range(len(list_taxon)):
        item = list_taxon[i]
        if not "[" in item:
            continue
        its = re.split('[\[\]]', item)
        rank = its[1]
        name = its[2].strip()
        if rank == "species":
            genus = name.split()[0]
            if genus in dic_gR and name not in list_sp:
                list_sp.append(name)
    return list_sp

# @input
# inputf: input fasta file
# list_sp: a list stores species names
# sp_dist: a dir where species files store sequences
# @return: None
# Assign sequences to species
def assign(inputf, list_sp, sp_dist):
    ck(inputf)
    with open(inputf) as f:
        items = f.read().splitlines()
    dic_seqs = {}
    for i in range(int(len(items)/2)):
        title = items[i*2]
        seq = items[i*2+1].replace("-", "")
        if len(seq) < 20000 and len(seq) > 250:
            dic_seqs[title] = seq
    log_writer('***Assignment starts!***\n...')
    for i in range(len(list_sp)):
        sp_name = list_sp[i].replace(" ", "_").replace("'", "").replace("/", "_")
        sp_jg1 = " "+list_sp[i]+" "
        sp_jg2 = "|"+list_sp[i]+"|"
        sp_f = sp_dist+sp_name+'.fasta'
        flag = False
        with open(sp_f, 'w+') as outf:
            for title in dic_seqs:
                seq = dic_seqs.get(title)
                if sp_jg1 in title or sp_jg2 in title:
                    flag = True
                    outf.write(title.replace(":", "_")+'\n'+seq+"\n")
        if flag == False:
            os.remove(sp_f)
        print("Assignment of species "+sp_name+" finished!")
    os.remove(inputf)
    log_writer('***Assignment ends successfully!***')

# @input
# hs_lib_dir: a dir stores the lib file of hs-blastn, which detect the similarity and coverage of sequences across species
# ref_hs: the reference file
# @return: None
def doTrim(hs_lib_dir, sp_dist, ref_hs, similarity_threshold_hs, coverage_threshold_hs, is_trim):
    hs_lib = hs_lib_dir+"lib.fasta"
    os.system("seqkit seq -w 0 "+ref_hs+" > "+hs_lib)
    with open(hs_lib) as f:
        items_ref = f.read().splitlines()

    dic_ref = {}
    for i in range(len(items_ref)-1):
        item = items_ref[i]
        seq = items_ref[i+1]
        if item.startswith(">") and not seq.startswith(">"):
            dic_ref[i] = (item.replace(" ","_")+"_"+str(len(seq)),seq,)

    with open(hs_lib,"w+") as f:
        for i in dic_ref:
            item=dic_ref.get(i,("null","null"),)
            f.write(item[0]+'\n'+item[1]+'\n')

    os.system("hs-blastn index "+hs_lib)
    list_sp_dist = os.listdir(sp_dist)
    for sp in list_sp_dist:
        if not sp.startswith("temp_"):
            sp_f = sp_dist+sp
            doTrimOn(sp_f, hs_lib, similarity_threshold_hs, coverage_threshold_hs, is_trim)

# @input
# similarity_threshold_hs and coverage_threshold_hs are both parameters in config file
# @return: None
def doTrimOn(sp_f, hs_lib, similarity_threshold_hs, coverage_threshold_hs, is_trim):
    with open(sp_f) as f:
        items_sp = f.read().splitlines()

    dic_temp_hs_sp = {}
    for i in range(len(items_sp)-1):
        item = items_sp[i]
        seq = items_sp[i+1]
        if item.startswith(">") and not seq.startswith(">"):
            dic_temp_hs_sp[item] = seq
    classify_hs(hs_lib, sp_f)

    with open("hs.COI") as f:
        items_hs_sp = f.read().splitlines()

    with open(sp_f, "w+") as f:
        for i in range(len(items_hs_sp)):
            item = items_hs_sp[i]
            if not item.startswith("#"):
                title = ">"+items_hs_sp[i-4].replace("# Query: ","")
                its = item.split("\t")
                simi = float(its[2])
                length = int(its[1].rsplit("_",1)[1])
                coverage = float(int(its[3])/length*100)
                if simi > similarity_threshold_hs and coverage > coverage_threshold_hs:
                    s_start = int(its[8])
                    s_end = int(its[9])
                    seq=dic_temp_hs_sp.get(title)
                    if is_trim == True:
                        q_start = int(its[6])-1
                        q_end = int(its[7])
                        seq=seq[q_start:q_end]
                    elif is_trim >= 1000:
                        q_start = int(its[6])-1
                        q_end = int(its[7])
                        if q_start > is_trim:
                            seq=seq[q_start:q_end]
                    if s_start > s_end:
                        seq = rev_comp(seq)
                    f.write(title+'\n'+seq+'\n')


# @input
# inputf: input fasta file
# taxonf: taxon file prodeced with taxonkit
# BOLDf: BOLD file
# sp_dist: A dir where species files store sequences
# @return: A dic stored with {genus:(family,order,clazz)}
def speciesSeparater(inputf, taxonf, BOLDf, sp_dist, hs_lib_dir, bar_type, ref_hs, similarity_threshold_hs, coverage_threshold_hs, is_trim):
    typeSearch(inputf, bar_type)
    alls = checkClazz(taxonf)
    tuple1 = genusRegister(alls, BOLDf)
    list_sp = speciesListMaker(alls, tuple1)
    assign(inputf, list_sp, sp_dist)
    if ref_hs.strip() != "":
        doTrim(hs_lib_dir, sp_dist, ref_hs, similarity_threshold_hs, coverage_threshold_hs, is_trim)
    return tuple1[0]


