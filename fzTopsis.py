#!/usr/bin/python3
'''
* ftopsis - program to compute Fuzzy TOPSIS ratings

'''
import pandas as pd
import pprint
import math
from tabulate import tabulate

pp = pprint.PrettyPrinter(width=41, compact=True)

# Functions  ----------------------------------------
def D(a,b):
    d = math.sqrt(((a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1]) + (a[2]-b[2])*(a[2]-b[2]))/3)
    return d

# Initialize ----------------------------------------
rScale = {"A":(0.75,0.9,1.0), "B":(0.5, 0.75, 0.9), "C":(0.3, 0.5, 0.75),\
          "D":(0.1, 0.3, 0.5), "F":(0.0, 0.1, 0.3)}

#pp.pprint(rScale)
# Read Wt
attrib = {"APL":{"Wt":0.362, "Desc":"Air Pollution Control"},
          "WPL":{"Wt":0.139, "Desc":"Water Pollution Control"},
          "BD" :{"Wt":0.185, "Desc":"Bio-diversity Measures"},
          "TBL":{"Wt":0.082, "Desc":"Trade Balance"},
          "FISC":{"Wt":0.067,"Desc":"Fiscal Balance"},
          "INFRA":{"Wt":0.097,"Desc":"Infrastructure"},
          "SNS":{"Wt":0.068, "Desc":"Safety and Security"}
          }
#pp.pprint(attrib)          
# Read ratings 
ratings = pd.read_csv('ratings.csv')
pp.pprint(ratings)
alternatives = list(set(ratings["Alternative"]))
alternatives.sort()
experts = list(set(ratings["Expert"]))
experts.sort()

# Conv to FN
rFN = {}
for j, t in ratings.iterrows():
    tFN = {}
    for i, v in t.items():
        tFN[i]=v if i in ["Expert", "Alternative"] else list(rScale[v])
    rFN[j]=tFN
pp.pprint(rFN)
# Combine ratings
cFN = {}
for i in alternatives:
    cAttr = {}
    for j in attrib:
        a = []
        b = []
        c = []
        #print(i,j)
        for k in rFN:
            if rFN[k]["Alternative"]== i:
                a.append(rFN[k][j][0])
                b.append(rFN[k][j][1])
                c.append(rFN[k][j][2])
        ai = min(a)
        bi = sum(b)/len(b)
        ci = max(c)
        cAttr[j] = [ai,bi,ci]
    cFN[i] = cAttr
print("\nCombined Table\n")    
pp.pprint(cFN)        
# Normalize
cStar = {}
for a in attrib:
    cj = []
    for i in alternatives:
        cj.append(cFN[i][a][2])
    cStar[a] = max(cj)
print(cStar)    
nFN = cFN
for a in attrib:
    for i in alternatives:
        for j in [0,1,2]:
            nFN[i][a][j] = nFN[i][a][j]/cStar[a]
print("\nNormalized Table\n")                
pp.pprint(nFN)
# GET FPIS, FNIS
fpis = {}
fnis = {}
for a in attrib:
    fpis[a] = nFN[alternatives[0]][a]
    fnis[a] = nFN[alternatives[0]][a]
    for i in alternatives:
        fpis[a] = fpis[a] if fpis[a][1] >= nFN[i][a][1] else nFN[i][a]
        fnis[a] = fnis[a] if fnis[a][1] <= nFN[i][a][1] else nFN[i][a]
print("\n",80*"~")
print("FPIS")
pp.pprint(fpis)
print("\nFNIS")
pp.pprint(fnis)

# Compute CC
cc = {}
ranks = {}
posn = []
dp = {}
dn = {}
for i in alternatives:
    dplus = 0
    dminus = 0
    for a in attrib:
        dplus += attrib[a]["Wt"]*D(nFN[i][a], fpis[a])
        dminus += attrib[a]["Wt"]*D(nFN[i][a], fnis[a])
    cci = dminus/(dplus+dminus)
    posn.append(cci)
    cc[i] = cci
    dp[i] = dplus
    dn[i] = dminus
pp.pprint(cc)  
#pp.pprint(dp)
#pp.pprint(dn)
posn.sort(reverse=True)
for i in alternatives:
    ranks[i] = posn.index(cc[i]) + 1
pp.pprint(ranks)  
print("\n",80*"~")
# Result
print("Alternatives", end="& ")
for a in attrib:
    print(a, end="& ")
print("CCi&Rank\\\\")    
print("Wt", end="& ")
for a in attrib:
    print(attrib[a]["Wt"], end="& ")
print("CCi&Rank\\\\")    
for i in alternatives:
    print(i,end="& ")
    for a in attrib:
        print(nFN[i][a], end="&")
    print(cc[i], end="&")
    print(ranks[i], "\\\\")
print("FPIS", end="&")
for a in attrib:
    print(fpis[a], end="&")
print ("\\\\")

print("FNIS", end="&")
for a in attrib:
    print(fnis[a], end="&")
print ("\\\\")
