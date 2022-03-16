#!/usr/bin/python
import os
import sys
from shutil import copy as cp
from pys.hlNoneMatch import detSimi, readFN, detPP

group = sys.argv[1]
threshold_g = 80
threshold_f = 80
for i in range(1,101):
    print("pick "+str(i)+"...")
    path1 = 'test_accuracy/results/'+group+'/'+str(i)+'/'
    path2 = 'test_accuracy/_results/'+group+'/'+str(i)+'/'
    path3 = 'test_accuracy/results/'+group+'/'+'report'+'/'+str(i)+'/'
    #path3 = 'test/temp_dir_pre/'+group+'/'+str(i)+'/'
    source1 = path1+'vsearch_result.csv'
    source2 = path1+'hsblastn_result.csv'
    target1 = path2+'vsearch_result.csv'
    target2 = path2+'hsblastn_result.csv'
    if not os.path.exists(path2):
        os.mkdir(path2)
    detSimi(source1,target1,threshold_g,threshold_f)
    detSimi(source2,target2,threshold_g,threshold_f)
    #detPP(path1+'epang_result.csv',path3+'epang_result.csv',path2+'epang_result.csv')
    #detPP(path1+'rappas_result.csv',path3+'rappas_result.csv',path2+'rappas_result.csv')
    cp(path1+'epang_result.csv',path2+'epang_result.csv')
    cp(path1+'rappas_result.csv',path2+'rappas_result.csv')
    cp(path1+'apples_result.csv',path2+'apples_result.csv')

    readFN(path2, path3)
