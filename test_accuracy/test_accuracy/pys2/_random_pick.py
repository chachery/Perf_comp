#!/usr/bin/python
import os
import random

def r_pick(lib_file, test_ref, test_query, pick_times, genus_filter=True):
    temp = 'temp/'
    temp_grep = temp + 'temp_grep.txt'
    pick_times = int(pick_times)

    with open(lib_file) as lf:
        items = lf.read().splitlines()
        seqs_num = len(items)//2

    dic_genusNum = {}
    for item in items:
        if item.startswith(">"):
            genus=item[:item.find('_')]
            if genus not in dic_genusNum:
                dic_genusNum[genus] = 1
            else:
                dic_genusNum[genus] += 1

    
#    random_list = []
#    for i in range(seqs_num):
#        title=items[2*i]
#        genus=title[:title.find('_')]
#        os.system('grep "'+genus+'" '+lib_file+' > '+temp_grep)
#        f=open(temp_grep)
#        line=len(f.readlines())
#        f.close()
#        if line > 1:
#            random_list.append(i)
#    os.system('>'+temp_grep)

#    if genus_filter:
#        query_index = random.sample(random_list, pick_times)
#    else:
#        query_index = random.sample(range(seqs_num), pick_times)


    query_index = []
    while len(query_index) < pick_times:
        index = random.randint(0,seqs_num-1)
        title = items[2*index]
        genus=title[:title.find('_')]
        if index not in query_index and dic_genusNum[genus] > 1:
            query_index.append(index)
            dic_genusNum[genus] -= 1

    with open(test_query, 'w+') as tq:
        for i in query_index:
            tq.write(items[2*i]+'\n'+items[2*i+1]+'\n')

    with open(test_ref, 'w+') as tr:
        for i in range(seqs_num):
            if not i in query_index:
                tr.write(items[2*i]+'\n'+items[2*i+1]+'\n')
    
