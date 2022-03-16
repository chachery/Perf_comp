#!/usr/bin/python
import os
import random

def r_pick(lib_file, test_ref, test_query, pick_times, genus_filter=False):
    temp = 'temp/'
    temp_grep = temp + 'temp_grep.txt'
    pick_times = int(pick_times)

    with open(lib_file) as lf:
        items = lf.read().splitlines()
        seqs_num = len(items)//2

    random_list = []
    for i in range(seqs_num):
        title=items[2*i]
        genus=title[:title.find('_')]
        os.system('grep "'+genus+'" '+lib_file+' > '+temp_grep)
        f=open(temp_grep)
        line=len(f.readlines())
        f.close()
        if line > 1:
            random_list.append(i)
    os.system('>'+temp_grep)

    if genus_filter:
        query_index = random.sample(random_list, pick_times)
    else:
        query_index = random.sample(range(seqs_num), pick_times)

    with open(test_query, 'w+') as tq:
        for i in query_index:
            tq.write(items[2*i]+'\n'+items[2*i+1]+'\n')

    with open(test_ref, 'w+') as tr:
        for i in range(seqs_num):
            if not i in query_index:
                tr.write(items[2*i]+'\n'+items[2*i+1]+'\n')
