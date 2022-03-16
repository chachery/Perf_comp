#python3
import sys
import os
#以读入文件为例：
f = open(sys.argv[1],"rb")#二进制格式读文件
i = 0
list_rm = []
while True:
    i += 1 
    #print(i)
    line = f.readline()
    if not line:
        break
    else:
        try:
#             print(line)
#             print(line.decode('utf8'))
            line.decode('utf8')
            #为了暴露出错误，最好此处不print
        except:
            list_rm.append(i)

for j in reversed(list_rm):
    os.system('sed -i "'+str(j)+'d" '+sys.argv[1])
