import sys
with open(sys.argv[1]) as f:
    items_source = f.read().splitlines()

with open(sys.argv[2]) as f:
    items_target = f.read().splitlines()

dic_source = {}
for i in range(len(items_source)):
    if i % 2 == 0:
        dic_source[items_source[i]] = items_source[i+1]

with open(sys.argv[2], "w+") as f:
    for i in range(len(items_target)):
        if i % 2 == 0:
            item = items_target[i]
        else:
            #if items_target[i-1].startswith(">Arachnida_"):
            if sys.argv[2].endswith("query_me.fasta") or sys.argv[2].endswith("query.fasta"):
                its = items_target[i-1].split("_", 4)
                item = dic_source.get(">"+its[-2]+'_'+its[-1])
            else:
                item = dic_source.get(items_target[i-1])
        f.write(item+'\n')
