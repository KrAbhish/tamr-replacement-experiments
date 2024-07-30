import csv
import re
import editdistance
import numpy as np
import CustomerRec as rec

ctr = 0
legal={}
test={}
with open('export.csv', mode ='r')as file:
    csvFile = csv.reader(file)
    for arr in csvFile:
        ctr += 1
        if ctr <= 50000:
            if arr[1] in legal:
                master = legal[arr[1]]
                master.add_taxes(arr[27:33])
                master.add_bvd(arr[24:27])
                master.add_phone(arr[21])
                master.add_name(arr[4])
            else:
                legal[arr[1]] = rec.LegalMaster(arr[4], arr[27:32], arr[24:26], arr[21], arr[15], arr[11], arr[14])
        else:
            if arr[1] in test:
                test[arr[1]].append(arr)
            else:
                test[arr[1]] = [arr]

outf=open('Mis.csv','w')
def write_result(rec, arr):
    global outf
    line = 'T,'+str(arr)
    outf.write(line+'\n')
    lines = rec.to_string()
    for line in lines:
        outf.write('S'+line+'\n')
    
ctr = 0
ctr2 = 0
ctr3 = 0
for k,v in test.items():
    if k not in legal:
        if len(v) > 1:
            ctr3 += 1
        continue
    for itm in v:
        ctr2+=1
        res = legal[k].match(itm)
        if res is False:
            ctr += 1
            write_result(legal[k], itm)
            
        
print(ctr)
print(ctr2)
print(ctr3)
outf.close()