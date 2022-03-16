#!/usr/bin/python
import os
from pathlib import Path

# @input
# csvf: result csv file
# @return: A tuple contains seq_num, clas_score, order_score, family_score and genus_score
def getScores(csvf):
    with open(csvf) as f:
        items = f.read().splitlines()

    dic_scores = {}
    for item in items:
        if item.startswith("NO.;"):
            continue
        levels = item.split(";")
        num = levels[0]
        source_titles = levels[1].split("_", 4)
        score = 0
        if levels[7] == source_titles[3]:
            score = 4
        elif levels[6] == source_titles[2]:
            score = 3
        elif levels[5] == source_titles[1]:
            score = 2
        elif levels[4] == source_titles[0]:
            score = 1
        if num not in dic_scores:
            dic_scores[num] = score
        elif score > dic_scores[num]:
            dic_scores[num] = score

    seq_num = str(len(dic_scores))
    genus_score = sum(value == 4 for value in dic_scores.values())
    family_score = sum(value == 3 for value in dic_scores.values()) + genus_score
    order_score = sum(value == 2 for value in dic_scores.values()) + family_score
    clas_score = sum(value == 1 for value in dic_scores.values()) + order_score
    return (seq_num, str(clas_score), str(order_score), str(family_score), str(genus_score))

def getReportStorePath(csvf_path, sdir="report"):
    if csvf_path.endswith("/"):
        reportStorePath = csvf_path.rsplit("/",2)
    else:
        reportStorePath = csvf_path.rsplit("/",1)
    rSPath = reportStorePath[0] + '/' + sdir + '/' + reportStorePath[1]
    return rSPath

# @input
# csvf_path: a path stores csv files
# @return: None
def doExam(csvf_path):
    csvfs = os.listdir(csvf_path)
    reportStorePath = getReportStorePath(csvf_path)
    if not Path(reportStorePath).is_dir():
        os.makedirs(reportStorePath)
    for csvf in csvfs:
        scores_tuple = getScores(csvf_path + csvf)
        method = csvf.split("_")[0]
        reportf_name = reportStorePath + "/" + method + '.report'
        str_scores = '\t'.join(scores_tuple)
        with open(reportf_name, "w+") as f:
            f.write("Totally\ttoClass\ttoOrder\ttoFamily\ttoGenus\n" + str_scores + '\n')
        print(method + ":\nTotally\ttoClass\ttoOrder\ttoFamily\ttoGenus\n" + str_scores + '\n')
