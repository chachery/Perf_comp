#!/usr/bin/python
import os
from pathlib import Path
from pys.logAndPrint import logAndPrint
from pys.exam import getReportStorePath

log = "log/log"

# detect FN in pp-based methods
# source_u: csv files in <test_accuracy/results> (with "-U" option)
# source_unu: csv files n <test/temp_dir_pre/> (without "-U" option)
# target: csv file in <test_accuracy/_results>
def detPP(source_u, source_unu, target):
    with open(source_u) as f:
        items = f.read().splitlines()
    dic_scores = {}
    for item in items:
        if not item.startswith("NO."):
            its = item.split(";")
            levels = its[1].split("_")
            score = 0
            if levels[2] == its[6]:
                score = 1
            if levels[3] == its[7]:
                score = 2
            dic_scores[its[0]] = [score, item]
        else:
            dic_scores["0"] = [-1, item]

    with open(source_unu) as f:
        items_unu = f.read().splitlines()
    dic_items = {}
    for item in items_unu:
        if not item.startswith("NO."):
            its = item.split(";")
            o_f = "_".join([its[5], its[6]])
            if its[0] not in dic_items:
                dic_items[its[0]] = [o_f,]
            else:
                dic_items[its[0]].append(o_f)

    print("Alter (from "+source_unu+"):")
    for item in dic_items:
        list1 = dic_items.get(item, [])
        len_item = len(list1)
        if len_item == 0:
            print("Warning: in seq "+item)
        elif len_item > 1:
            score = dic_scores.get(item, [-1,])[0]
            varity = tecSameLevel(list1)
            if score == -1:
                print("Warning: in seq "+item)
            elif score == 1:
                it = dic_scores.get(item)[1]
                its = it.split(";")
                its[7] = "null"
                dic_scores[item][1] = ";".join(its)
                #print(dic_scores[item][1])
            elif score == 0:
                it = dic_scores.get(item)[1]
                its = it.split(";")
                if varity == 2:
                     its[5] = "null"
                if varity > 0:
                     its[6] = "null"
                its[7] = "null"
                dic_scores[item][1] = ";".join(its)
                #print(dic_scores[item][1])

    with open(target, "w+") as f:
        for tp in dic_scores:
            item = dic_scores.get(tp)[1]
            f.write(item+'\n')
            

def tecSameLevel(list1):
    orders = []
    familys = []
    for item in list1:
        its = item.split("_")
        if its[0] not in orders:
            orders.append(its[0])
        if its[1] not in familys:
            familys.append(its[1])
    if len(orders) > 1:
        return 2
    elif len(familys) >1:
        return 1
    else:
        return 0


# detect FN in similarity-based methods
# source: csv files in <test_accuracy/results>
# target: csv file in <test_accuracy/_results>
# threshold: wrong assignments below similarity-threshold would be considered as FN.
def detSimi(source, target, threshold_g, threshold_f):
    with open(source) as f:
        items = f.read().splitlines()

    with open(target,"w+") as f:
        for item in items:
            if not item.startswith("NO."):
                its = item.split(";")
                title = its[1].split("_")
                simi = its[-2].replace("%","")
                nb = int(its[0])
                try:
                    simi = float(simi)
                    if simi < threshold_f and simi > 50 and its[6] != title[2]:
                        for n in range(2,7):
                            its[n] = "null"
                    if simi < threshold_g and simi > 50 and its[7] != title[3]:
                        its[7] = "null"
                        its[8] = "null"
                    item = ";".join(its)
                except ValueError:
                    logAndPrint(log, 'Warning: file["'+source+'"], seq '+str(nb)+' has illegal similarity value!')
            f.write(item+'\n')

# count FN and FP
# the path stores csv file in <tets_accuray/_results>
def readFN(csvf_path, csvf_path2):
    csvfs = os.listdir(csvf_path)
    reportStorePath = getReportStorePath(csvf_path)
    if not Path(reportStorePath).is_dir():
        os.makedirs(reportStorePath)
    for csvf in csvfs:
        flag = False
        if csvf.startswith("epang") or csvf.startswith("rappas") or csvf.startswith("apples"):
            flag = True
        list_FN = countFN(csvf_path2+csvf.replace("_result.csv", ".report"))
        with open(csvf_path+csvf) as f:
            items = f.read().splitlines()
        method = csvf.split("_")[0]
        reportf_name = reportStorePath + "/" + method + '.report'
        num_total = len(items)-1
        null_genus = null_family = null_order = 0
        for item in items:
            if not item.startswith("NO."):
                switch = False
                its = item.split(";")
                levels = its[1].split("_")
                if flag == False and its[6] == "null":
                    null_family += 1
                elif flag == True and its[6] == "null" and its[5] in (levels[1], 'null'):
                    null_family += 1
                    switch = True
                if flag == False and its[7] == "null":
                    null_genus += 1
                elif flag == True and its[7] == "null" and (its[6] == levels[2] or switch == True):
                    null_genus += 1
                if its[5] == "null":
                    null_order += 1
        FP_family = list_FN[1]-null_family
        FP_genus = list_FN[2]-null_genus
        with open(reportf_name, "w+") as f:
            f.write("Totally\tFN_order\tFN_family\tFN_genus\tFP_family\tFP_genus\n" + str(num_total) + '\t' + str(list_FN[0]) + '\t' + str(list_FN[1]) + '\t' + str(list_FN[2]) + '\t' + str(FP_family) +'\t' + str(FP_genus) + '\n')
        print(method + ":\nTotally\tFN_order\tFN_family\tFN_genus\tFP_family\tFP_genus\n" + str(num_total) + '\t' + str(list_FN[0]) + '\t' + str(list_FN[1]) + '\t' + str(list_FN[2]) + '\t' + str(FP_family) +'\t' + str(FP_genus) + '\n')

# count FN
# the path stores csv file in <tets_accuray/results>
def countFN(reportf):
    with open(reportf) as f:
        items = f.read().splitlines()
    list_FN = items[1].split("\t")
    SUM = int(list_FN[0])
    return [SUM-int(i) for i in list_FN[2:]]

# count TN
# befPick_f: count sequence number among all genus in <test_accuracy/lib/$xxx/name.label> (file)
# aftPick_p: count sequence number among all genus in <test_accuracy/test_lib/$xxx/$i/test_query.fasta> (path;$xxx)
def readTN(befPick_f, aftPick_p):
    with open(befPick_f) as f:
        items = f.read().splitlines()
    dic_befPick = {}
    for item in items:
        its = item.split(";")
        genus = its[-2]+"_"+its[-1]
        if genus not in dic_befPick:
            dic_befPick[genus] = 1
        else:
            dic_befPick[genus] += 1
    taxon = befPick_f.split("/")[-2]
    logAndPrint(log, 'Now loding taxon... <'+taxon+'>')
    for i in range(1,21):
        logAndPrint(log, "Pick "+str(i))
        dic_aftPick = {}
        with open(aftPick_p+'/'+str(i)+'/test_query.fasta') as f:
            seqs = f.read().splitlines()
        for seq in seqs:
            if seq.startswith(">"):
                levels = seq.split("_")
                genus = levels[2]+'_'+levels[3]
                if genus not in dic_aftPick:
                    dic_aftPick[genus] = 1
                else:
                    dic_aftPick[genus] += 1
        TN_genus = []
        for g in dic_aftPick:
            if dic_aftPick[g] == dic_befPick[g]:
                TN_genus.append(g)
        TN_number = 0
        for g in TN_genus:
            TN_number += dic_befPick[g]
        logAndPrint(log, "Pick "+str(i)+'... TN number: '+str(TN_number))
        for g in TN_genus:
            logAndPrint(log, g)
        logAndPrint(log,'')
