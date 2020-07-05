#!/usr/bin/env python
from sys import argv
import re
import xml.etree.ElementTree as ET
import numpy as np
import random
#import GenerateTree


class ReadInput:
    varList = []
    constrscope = {}
    adjancencyDic = {}
    constrrelation = {}
    nvalues = 0
    construtilTable = {}
    scopeConstrTable = {}
    elicitationCostTable = {}

    incompleteConstrTable = {}
    varDomainList = {}
    maxQuestions = 0
    maxQ = 0
    allcostList = []

    path = ""
    name = ""

    def __init__(self, xmlfile, path, name):
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        self.path = path
        self.name = name
        low_n = 1
        high_n = 20

        for ch in root:
            if ch.tag == 'domains':
                domTag = ch.find('domain')
                self.nvalues = int(domTag.get('nbValues'))

            elif ch.tag == 'variables':
                allvars = ch.findall('variable')
                for v in allvars:
                    self.varList.append(int(v.get('name')))
                    self.varDomainList[int(v.get('name'))] = [d for d in range(1, self.nvalues +1)]

                for i in range(len(allvars)):
                    v = allvars[i]

            elif ch.tag == 'relations':

                relations = ch.findall('relation')
                for c in relations:
                    utable = c.text
                    urows = utable.split('|')
                    self.constrrelation[c.get('name')] = urows

            elif ch.tag == 'constraints':
                contrs = ch.findall('constraint')
                for c in contrs:
                    self.constrscope[c.get('reference')] = c.get('scope')

        for n in self.constrrelation:
            constrtable = np.zeros(shape=(self.nvalues, self.nvalues), dtype='U16')
            elcCostTable = np.zeros(shape=(self.nvalues, self.nvalues), dtype=int)
            ut = self.constrrelation[n]
            utls = {}
            for u in ut:
                udim = u.split(':')
                vals = udim[1].split(' ')

                constrtable[int(vals[0])-1][int(vals[1])-1] = udim[0]
                elcCostTable[int(vals[0])-1][int(vals[1])-1] = int(np.random.uniform(low_n,high_n,None))

            self.scopeConstrTable[self.constrscope[n]] = constrtable
            self.elicitationCostTable[self.constrscope[n]] = elcCostTable

        for v in self.varList:
            nodelist = []
            for c1 in self.constrscope:
                scope1 = self.constrscope[c1].split(' ')
                if v == int(scope1[0]):
                    nodelist.append(int(scope1[1]))
                elif v == int(scope1[1]):
                    nodelist.append(int(scope1[0]))
            self.adjancencyDic[v] = nodelist

        #path = "/home/cdao/Atena/aaai2019/optimal/cop-ISBB/" 
        #path = ""
        outp = open(self.path+'oracle'+'-'+self.name+'.txt', 'w')
        #print("elicitationCostTable: ", self.elicitationCostTable )

        outp.write('Constraint-Tables: ')
        count1 = 0
        for k in self.scopeConstrTable:

            outp.write(str(k) + ': ')
            matrix = self.scopeConstrTable[k]
            c = 0
            for row in range(0, self.nvalues):
                for col in range(0, self.nvalues):

                    if c < (self.nvalues * self.nvalues) - 1:
                        outp.write(str(matrix[row][col]) + ' ')
                    else:
                        outp.write(str(matrix[row][col]).trim())
                c += 1
            if count1 < len(self.scopeConstrTable) - 1:
                outp.write('; ')

            count1 += 1
        outp.close()
        #outp.write('\n')


    def calculate_costAtLeaf(self, var, val, parentsValues, scopeConstrTable):

        #print(var, val)
        #print(self.adjancencyDic)
        #print(self.scopeConstrTable)
        neighborsList = self.adjancencyDic[int(var)]
        #print 'neighbors: ', neighborsList, parentsValues
        sumCost = []
        questionMarkNo = 0
        maxSumCost = 0

        for p in parentsValues:
            if p in neighborsList:
                sc = str(p) + ' ' + str(var)
                pval = parentsValues[p]
                if sc not in scopeConstrTable:
                    sc = str(var) + ' ' + str(p)
                    if sc in scopeConstrTable:
                        costMat = scopeConstrTable[sc]
                        cost = costMat[int(val) - 1][int(pval) - 1]
                    else:
                        continue

                else:
                    costMat = scopeConstrTable[sc]
                    cost = costMat[int(pval) - 1][int(val) - 1]

                if cost == '?':
                    questionMarkNo += 1
                else:
                    maxSumCost = maxSumCost + int(cost)

                sumCost.append(cost)

        #print('leaf: ', val ,sumCost)
        checkConstraints = []
        for p in parentsValues:
            for p1 in parentsValues:
                sc = str(p) + ' ' + str(p1)
                sc1 = str(p1) + ' ' + str(p)
                if p!= p1 and (sc in scopeConstrTable or sc1 in scopeConstrTable):
                    sc = str(p) + ' ' + str(p1)

                    if sc not in scopeConstrTable:
                        sc1 = str(p1) + ' ' + str(p)

                        if sc1 in scopeConstrTable:
                            costMat = scopeConstrTable[sc1]
                            cost = costMat[int(parentsValues[p1]) - 1][int(parentsValues[p]) - 1]
                        else:
                            continue
                    else:
                        costMat = scopeConstrTable[sc]
                        cost = costMat[int(parentsValues[p]) - 1][int(parentsValues[p1]) - 1]

                    if sc not in checkConstraints or sc1 not in checkConstraints and (sc1 in scopeConstrTable or sc in scopeConstrTable):

                        if cost == '?':
                            questionMarkNo += 1
                        else:
                            maxSumCost = maxSumCost + int(cost)

                        sumCost.append(cost)
                        checkConstraints.append(sc)
                        checkConstraints.append(sc1)

        return sumCost, questionMarkNo, maxSumCost


    def createIncompleteConstrTable(self, all, incompleteness, nvalues, scopeConstrTable):

        self.incompleteConstrTable = scopeConstrTable
        incompList = []
        dt = '?'
        if all:
            while len(incompList) == 0 or ( len(incompList) < incompleteness):
                row = random.randint(0, int(nvalues) - 1)
                col = random.randint(0, int(nvalues) - 1)
                whichconstr = random.randint(0, len(scopeConstrTable) - 1)

                countK = 0

                for k in self.incompleteConstrTable.keys():
                    if countK == whichconstr:
                        constrtable = scopeConstrTable[k]
                        constrtable[row][col] = dt
                        self.incompleteConstrTable[k] = constrtable

                    countK += 1
                if (whichconstr, row, col) not in incompList:
                    incompList.append((whichconstr, row, col))
                    self.maxQuestions += 1



        else:
            incompPerConstr = int(round(float(incompleteness/100.0) * (nvalues ** 2)))

            for k in self.incompleteConstrTable.keys():
                incompList = []
                while len(incompList)== 0 or ( len(incompList) < incompPerConstr):
                    row = random.randint(0, int(nvalues) - 1)
                    col = random.randint(0, int(nvalues) - 1)
                    constrtable = scopeConstrTable[k]

                    constrtable[row][col] = dt
                    self.incompleteConstrTable[k] = constrtable


                    if (k, row, col) not in incompList:
                        incompList.append((k, row, col))
                        self.maxQuestions += 1
            #print(incompPerConstr, round(float(incompleteness / 100.0), (nvalues ** 2)),self.maxQuestions)
        return self.incompleteConstrTable

    def createElicitCost(self):
        outp1 = open(self.path + 'elicit' + '-' + self.name + '.txt', 'w')
        outp1.write('ElicitationCost-Tables: ')
        count1 = 0
        for k in self.elicitationCostTable:

            outp1.write(str(k) + ': ')
            matrix = self.elicitationCostTable[k]
            c = 0
            for row in range(0, self.nvalues):
                for col in range(0, self.nvalues):

                    if c < (self.nvalues * self.nvalues) - 1:
                        outp1.write(str(matrix[row][col]) + ' ')
                    else:
                        outp1.write(str(matrix[row][col]).trim())
                c += 1
            if count1 < len(self.elicitationCostTable) - 1:
                outp1.write('; ')
            count1 += 1
        outp1.close()

    def createIncompleteProblem(self):
        #path= "/home/cdao/Atena/aaai2019/optimal/cop-ISBB/"
        #path = ""
        outp = open(self.path+'output-Incomp'+'-'+self.name+'.txt','w')

        outp.write('Variables: ')
        for i  in range(0,len(self.varList)):
            if i< len(self.varList)-1:
                outp.write(str(self.varList[i])+'; ')
            else:
                outp.write(str(self.varList[i])+'\n')

        outp.write('Variable-Domain: ')
        count = 0
        for i in self.varDomainList:
            outp.write(str(i) + ': ')
            for d in self.varDomainList[i]:
                outp.write(str(d) + ' ')

            if count < len(self.varDomainList) - 1:
                outp.write('; ')

            else:
                outp.write('\n')
            count +=1

        outp.write('Constraint-Tables: ')
        count1 = 0
        for k in self.incompleteConstrTable:

            outp.write(str(k)+ ': ')
            matrix = self.incompleteConstrTable[k]
            c = 0
            for row in range(0,self.nvalues):
                for col in range(0, self.nvalues):
                    if c < (self.nvalues * self.nvalues)-1:
                        outp.write(str(matrix[row][col])+' ')
                    else:
                        outp.write(str(matrix[row][col]).trim())
                c +=1
            if count1 < len(self.incompleteConstrTable)-1:
                outp.write('; ')

            count1 +=1
        outp.write('\n')
        outp.write('Number of missings: '+ str(self.maxQuestions))

        outp.close()

    def readIncomp(self, incompFile):
        varList = []
        varDomain = {}
        incompConstCost = {}
        nvalues = 0
        for l in incompFile.readlines():
            if re.search('Variables: ',l):
                vr = l.replace('Variables: ','')
                vars = vr.split(';')
                varList = [int(v) for v in vars]

            elif re.search('Variable-Domain: ',l):
                vd = l.replace('Variable-Domain: ','')
                vv = vd.split(';')
                for v in vv:
                    varDom = v.split(':')
                    doms = varDom[1].split(' ')
                    lst = []
                    for d in doms:
                        if d.strip()!='':
                            lst.append(d.strip())
                    varDomain[int(varDom[0].strip())] = lst

            elif re.search('Constraint-Tables: ',l):
                constr = l.replace('Constraint-Tables: ', '')
                contrkeysCost = constr.split(';')

                for kc in contrkeysCost:
                    kcost = kc.split(':')
                    costs = kcost[1].split(' ')
                    costList = []
                    for c in costs:
                        if c!='':
                            costList.append(c)

                    incompConstCost[kcost[0].strip()] = costList

            elif re.search('Number of missings: ',l):
                nQ = l.replace('Number of missings: ', '')
                self.maxQ = int(nQ)


        ## if number of values are the same for all variables
        nvalues = len(varDomain[0])

        incompleteCostTable = {}
        for k in incompConstCost:
            costs = incompConstCost[k]
            matrix = np.zeros(shape=(nvalues, nvalues), dtype='U16')
            count = 0
            for i in range(0,nvalues):
                for j in range(0, nvalues):

                    matrix[i][j] = costs[count]
                    count +=1

            incompleteCostTable[k] = matrix

        return incompleteCostTable,varList, varDomain

    def readOracle(self, oracleFile, nvalues):

        oracleConstCost = {}
        rf = oracleFile

        for l in rf.readlines():
            if re.search('Constraint-Tables: ', l):
                constr = l.replace('Constraint-Tables: ', '')
                contrkeysCost = constr.split(';')

                for kc in contrkeysCost:
                    kcost = kc.split(':')
                    costs = kcost[1].split(' ')

                    costList = []
                    for c in costs:
                        if c != ' ' and c != '' and c != '\n':
                            costList.append(c)

                    oracleConstCost[kcost[0].strip()] = costList
                    #print(kcost[0].strip(), costList)
                    for u in costList:
                        if int(u) not in self.allcostList:
                            self.allcostList.append(int(u))

            elif re.search('\n', l):
                break
            else:
                break

        oracleCostTable = {}
        for k in oracleConstCost:
            costs = oracleConstCost[k]
            matrix = np.zeros(shape=(nvalues, nvalues), dtype='U16')
            count = 0
            for i in range(0, nvalues):
                for j in range(0, nvalues):
                    matrix[i][j] = costs[count]
                    count += 1

            oracleCostTable[k] = matrix
        #print('Read oracle: ', oracleFile, oracleFile.readlines())
        return oracleCostTable

    def readElicitationCost(self, f, nvalues):

        elcCostTables = {}

        oracleConstCost = {}
        #print('Read Elc: ',oracleFile)
        for l in f.readlines():
            #print('Say something')
            if re.search('ElicitationCost-Tables: ', l):
                #print(l)
                constr = l.replace('ElicitationCost-Tables: ', '')
                contrkeysCost = constr.split(';')

                for kc in contrkeysCost:
                    kcost = kc.split(':')
                    costs = kcost[1].split(' ')

                    costList = []
                    for c in costs:
                        if c != ' ' and c != '' and c != '\n':
                            costList.append(c)

                    oracleConstCost[kcost[0].strip()] = costList
                    #print( kcost[0].strip() , costList)
                    # for u in costList:
                    #     if int(u) not in self.allcostList:
                    #         self.allcostList.append(int(u))

        elcCostTables = {}
        for k in oracleConstCost:
            costs = oracleConstCost[k]
            matrix = np.zeros(shape=(nvalues, nvalues), dtype=int)
            count = 0
            for i in range(0, nvalues):
                for j in range(0, nvalues):
                    matrix[i][j] = costs[count]
                    count += 1

            elcCostTables[k] = matrix

        return elcCostTables

def main():
    xmlfile = open(argv[1], 'r')
    if int(argv[2]) == 1: all = True
    else: all = False
    incompletenessNo = int(argv[3])
    path = ""
    path = str(argv[4])
    ###read input xml file as the given problem
    name = str(argv[5])


    input = ReadInput(xmlfile, path, name)

    scopeConstrTable = input.createIncompleteConstrTable(all, incompletenessNo, input.nvalues, input.scopeConstrTable)
    input.createElicitCost()
    #generate Incomplete problem (randomly replace costs with ?s )
    input.createIncompleteProblem()


if __name__ == '__main__':
    main()