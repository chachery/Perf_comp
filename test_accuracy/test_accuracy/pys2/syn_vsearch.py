#!/usr/bin/python
#Remove the sequences which included in the query_file from lib_file and output result_file as result.
import os
def syn(lib_file, query_file, result_file):
  with open(lib_file) as lf:
    items = lf.read().splitlines()

  with open(query_file) as qf:
    rm_targets = qf.read().splitlines()

  cp_items = items[:]

  for j in range(len(items)):
    if j % 2 == 0:
      nameOf_item = items[j].replace("__","_")
      seqOf_item = items[j+1]
      for k in range(len(rm_targets)):
        if k % 2 == 0:
          nameOf_rm = rm_targets[k]
          if nameOf_rm == nameOf_item:
            cp_items.remove(items[j])
            cp_items.remove(seqOf_item)
            break

  with open(result_file, 'w+') as rf:
    for i in cp_items:
      rf.write(i+'\n')
