#!/usr/bin/python
import os
import sys

def sameTitleTreater(inputf):
    with open(inputf) as f:
        items = f.read().splitlines()

    titleList=[]
    for item in items:
        if item.startswith(">"):
            if not item in titleList:
                titleList.append(item)
            else:
                i = 1
                title = item
                while True:
                    if title in titleList:
                        title = item + "(" + str(i) +")"
                        i += 1
                    else:
                        break
                titleList.append(title)
        else:
            titleList.append(item)

    with open(inputf,'w+') as f:
        for i in titleList:
            f.write(i + '\n')

def oneLineQSTreater(inputf, outputf):
    with open(inputf) as f:
        items = f.read().splitlines()

    dic_seqs = {}
    if not items[0].startswith(">"):
        sys.exit(1)
    i = 0
    for item in items:
        if item.startswith(">"):
            i += 1
            item = item.replace(" ","_").replace(";",",").replace("__","_")
            dic_seqs[i] = [item, '']
        else:
            dic_seqs[i][1] += str(item)
    with open(outputf, "w+") as f:
        for i in dic_seqs:
            f.write(dic_seqs[i][0]+'\n'+dic_seqs[i][1]+'\n')
    sys.exit(0)
