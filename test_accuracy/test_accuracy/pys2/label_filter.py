#!/usr/bin/python
import os
import sys

def label_filter(init_label, test_label, test_query):
    #labels file that collect labels which were filtered.
    filtered_label = 'filtered.label'
    with open(init_label) as f:
        labels = f.read().splitlines()

    with open(test_query) as f:
        seqs_and_titles = f.read().splitlines()
    
    be_filtered_labels=[]
    for i in range(len(seqs_and_titles)//2):
        be_filtered_title = seqs_and_titles[i*2][1:]
        be_filtered_labels.append(be_filtered_title)

    result_labels=[]
    dic_toFamily={}
    for i in range(len(labels)):
        label_title = labels[i].split('\t')[0]
        if not label_title in be_filtered_labels:
            result_labels.append(labels[i])
        else:
            family = labels[i].split(';',5)[4]
            order = labels[i].split(';',5)[3]
            clas = labels[i].split(';',5)[2]
            f_g_s = '>'+ clas + '_' + order + '_' + family + '_' + label_title
            dic_toFamily['>'+label_title] = f_g_s

    #print(str(dic_toFamily))
    with open(test_label, 'w+') as f:
        for i in range(len(result_labels)):
            f.write(result_labels[i]+'\n')

    with open(test_query, 'w+') as f:
        for i in range(len(seqs_and_titles)):
            if i % 2 == 1:
                f.write(seqs_and_titles[i]+'\n')
            else:
                new_label = dic_toFamily.get(seqs_and_titles[i], 'ErrorOccur')
                if new_label == 'ErrorOccur':
                    print(seqs_and_titles[i])
                    sys.exit('ErrorOccur: Please check your sequences and labels!')
                else:
                    f.write(new_label+'\n')
