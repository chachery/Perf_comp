#!/usr/bin/python
import sys
import os

inputf = sys.argv[1]
outputf = sys.argv[2]

#for i in "āáǎàōóǒòêēéěèīíǐìūúǔùǖǘǚǜü":
for i in "äüö":
    os.system("sed -i 's/"+i+"/u/g' "+inputf)

with open(inputf) as f:
    items = f.read().splitlines()

#list_family = []
dic_sp_family = {}
for item in items:
    if not item.startswith('processid'):
        its = item.split('\t')
        if len(its) < 21:
            print(item)
            continue
        levels = "__".join([its[11],its[13],its[15],its[21]])
        if "____" not in levels and not levels.endswith("__"):
            family = "__".join([its[11],its[13],its[15]])
            sp_name = its[21]
            if family not in dic_sp_family:
                dic_sp_family[family] = []
            if sp_name not in dic_sp_family[family]:
                dic_sp_family[family].append(sp_name)

with open(outputf, 'w+') as f:
    old_clazz = ""
    old_order = ""
    for family in sorted(dic_sp_family):
        clazz = family.split("__")[0]
        order = family.split("__")[1]
        fam = family.split("__")[2]
        if clazz != old_clazz:
            f.write('[class]\t'+clazz+'\n')
        if order != old_order:
            f.write('[order]\t'+order+'\n')
        f.write('[family]\t'+fam+'\n')
        old_clazz = clazz
        old_order = order
        for sp in dic_sp_family[family]:
            f.write('[species]\t'+sp+'\n')


