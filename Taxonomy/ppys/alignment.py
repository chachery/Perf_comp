#!/usr/bin/python3
#This script was not written by myself!
#Sorry for forgetting where I download from!
 
import sys
from Bio import SeqIO

#convert fasta to phylip
def f2p(fastaf, phylipf):
    sequence_list = [] # To keep order of sequence
 
    sequence_dict = {}
    for record in SeqIO.parse(open(fastaf, "r"), "fasta"):
        sequence_list.append(record.id)
        sequence_dict[record.id] = str(record.seq)
 
# Test length of the alignment:
    alignment_length = 0
    for gene in sequence_dict:
        if (alignment_length != 0) and (len(sequence_dict[gene]) != alignment_length):
            print("Error in alignment length, exit on error !!!")
            sys.exit()
        else:
            alignment_length = len(sequence_dict[gene])
 
    number_of_seq = len(sequence_dict)
 
    longest_id = sorted(sequence_dict.keys())[-1]
 
# Write alignment in Phylip format
    phyfile = open(phylipf, "w")
    phyfile.write(str(number_of_seq)+" "+str(alignment_length)+"\n")
 
    for gene in sequence_list:
        phyfile.write(gene.ljust(len(longest_id), ' ') + "   " + sequence_dict[gene] + "\n")
    phyfile.close()

    return getLen(fastaf)

#convert phylip to fasta
def p2f():
    with open("papara_alignment.default") as f:
        items = f.read().splitlines()
    dic = {}
    for i in range(len(items)):
        if not i == 0:
            item = items[i]
            its = item.split(" " * item.count(" "))
            dic[i-1] = (">"+its[0],its[1])
    return dic

#write seqs after alignment into ref and query
def seqSep(temp_dir,len_lib):
    dic_sp = p2f()
    with open(temp_dir+'/lib_pp.fas','w+') as f1:
        for i in range(len_lib):
            f1.write(dic_sp[i][0]+'\n'+dic_sp[i][1]+'\n')
    with open(temp_dir+'/query.fas','w+') as f2:
        for i in range(len_lib, len(dic_sp)):
            f2.write(dic_sp[i][0]+'\n'+dic_sp[i][1]+'\n')

#get length
def getLen(inputf):
    with open(inputf) as f:
        items = f.read().splitlines()
    return len(items)
