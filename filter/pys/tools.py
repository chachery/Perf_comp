#!/usr/bin/python
import sys
import os
from .error_df import WrongfastaException
from .colorfulWriter import warning_writer, error_writer

#用于核对fasta文件的单双行是否分别为标题和序列
#To ensure singular line is id and the another is sequence. 
def ck(f_c):
    flag=False
    try:
        with open(f_c) as fc:
            cf=fc.read().splitlines()
        for i in range(len(cf)):
            if i % 2 == 0 and not cf[i].startswith('>'):
                flag=True
            elif i % 2 == 1 and (cf[i].startswith('>') or cf[i].strip() == ""):
                flag=True
        if flag==True:
            raise WrongfastaException(flag)
    except WrongfastaException as e:
        warning_writer('Sorry: There are some mistakes in the fasta file '+f_c +'!')

#vsearch(default id_value:0.01)
def classify(a, b, c='0.01'):
    if 'result.COI' in os.listdir():
        os.system('>result.COI')
    cmd='vsearch --usearch_global '+b+' --db '+a+' --blast6out - --maxaccepts 0 --maxrejects 0 --id '+str(c)+' > result.COI'
    os.system(cmd)
    checkCOI()

#hs-blastn
def classify_hs(lib, query):
    if 'hs.COI' in os.listdir():
        os.system('>hs.COI')
    cmd='hs-blastn align -db '+lib+' -query '+query+' -out hs.COI -outfmt 7 -max_target_seqs 1'
    os.system(cmd)

#实现将序列以标题字母顺序排序
def sortByLetter(inputf):
    with open(inputf) as f:
        items = f.read().splitlines()

    #以标题为key，序列为value，制作字典
    dic={}
    for i in range(len(items)):
        if i % 2 == 0:
            if items[i].startswith(">"):
                dic[items[i]] = items[i+1]
            else:
                error_writer("Wrong fasta format!")

    #写入
    with open(inputf,'w+') as f:
        for title in sorted(dic):
            f.write(title+'\n'+dic.get(title,'error')+'\n')

#Count line num of a file:
def countLines(f1):
#    if os.path.exists(f1):
    with open(f1) as f:
        items = f.read().splitlines()
    return len(items)
#    else:
#        warning_writer('File ' + f1 + ' not found!')
#        return 0

#Get title (>class__order__family__genus__species) of sequence
def getTitle(sp_name, dic_gR):
    genus = sp_name.split("_")[0]
    species = sp_name.split("_", 1)[1]
    levels = dic_gR.get(genus)
    family = levels[0]
    order = levels[1]
    clazz = levels[2]
    title = "__".join([">"+clazz, order, family, genus, species])
    return title

#Get a dic with {title:seq}
def getSeqDic(inputf):
    with open(inputf) as f:
        items = f.read().splitlines()
    dic_seqs = {}
    for i in range(len(items)):
        if i % 2 == 0:
            title = items[i]
            seq = items[i+1]
            if title not in dic_seqs:
                dic_seqs[title] = seq
    return dic_seqs

#Check "result.COI"
def checkCOI():
    if not "result.COI" in os.listdir():
        warning_writer("No 'result.COI' available for specific species!")
    elif not os.path.getsize("result.COI"):
        warning_writer("'result.COI' is null for specific species!")

#Remove other type barcoding
def typeSearch(inputf, bar_type):
    if not bar_type.lower() == "all":
        with open(inputf) as f:
            items = f.read().splitlines()
        with open(inputf, "w+") as f:
            for i in range(len(items)):
                if i % 2 == 0:
                    title = items[i]
                    seq = items[i+1]
                    if bar_type in title or bar_type.upper() in title or bar_type.lower() in title:
                        f.write(title+"\n"+seq+"\n")

#Reverse complement
def rev_comp(seq):
    sc = ''
    bases = 'ACMRHBVDYKGT'
    for i in reversed(seq.upper()):
        if i in bases:
            index = bases.find(i)
            sc += bases[-1-index]
        else:
            sc += i
    return sc
