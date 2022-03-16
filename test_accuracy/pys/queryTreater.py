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
