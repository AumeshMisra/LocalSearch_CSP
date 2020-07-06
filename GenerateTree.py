#!/usr/bin/env python
from sys import argv
import sys
import re
import xml.etree.ElementTree as ET
from node import Node
from Tree import Tree
import readInput
import numpy as np
from numpy import linalg as LA
from SynchBB import SynchBB
from GraphNode import GraphNode
import copy
import time


class GenerateTree:

    def generate_tree_node(self,  node):

        #t.add_node(node)
        return node

    def generate_node(self, key, value, parent):

        nd = Tree(key, value, parent)
        #tupdated = self.generate_tree_node( nd)

        return nd#tupdated

    def tree_generator(self, gt, varList, domains, parentNode, stkParent):

        treeNodeList = []
        tempVarList = []
        tempVarList = varList

        parent = None
        value = None
        #print(varList)
        stackParents = stkParent


        if parentNode!= None:
            ind = tempVarList.index(parentNode)
            del tempVarList[ind]

        #print('temp Var List: ', tempVarList)

        for i in range(0, len(tempVarList)):

            if len(stackParents) == 0:

                for d in domains[varList[i]]:
                    key = (str(tempVarList[i]) + '-' + str(d))

                    tu = gt.generate_node(key, value, parent)

                    treeNodeList.append(tu)
                    if parent == None:
                        k = key
                    stackParents.append(k)
            else:
                auxstack = []
                while len(stackParents) != 0:
                    parent = stackParents.pop()
                    for d in domains[varList[i]]:
                        key = (str(tempVarList[i]) + '-' + str(d))
                        tu = gt.generate_node(key, value, parent)
                        #print(key, parent)
                        treeNodeList.append(tu)
                        # if key not in auxstack:
                        k = key + ';' + parent
                        auxstack.append(k)
                stackParents = auxstack

        return treeNodeList

    

    def costAt_leaves(self, input, varList, treeNodeList, scopeConstrTable):

        #print 'treeeNODE:::: varList:::: ', len(treeNodeList), varList
        leafNode = varList[len(varList) - 1]
        #print(leafNode)
        leafCostDic = {}
        constrCostList = []
        #print(input.scopeConstrTable)
        maxC = 0
        maxQ = 0
        sumList = []
        qNoList = []

        for t in treeNodeList:
            k, p = treeNodeList[t].get_key_parent()

            varVal = k.split('-')
            var = int(varVal[0])
            val = varVal[1]

            if var == leafNode:
                #print('k P: ', k, p)
                pList = p.split(';')

                pval = {}
                for i in pList:
                    vv = i.split('-')
                    pval[int(vv[0])] = vv[1]
                #key = k +':'+ p
                #constrCostList,qNo,sumCost = input.calculate_costAtLeaf(var, val, pval, scopeConstrTable)
                constrList = treeNodeList[t].get_relations()
                if len(constrList) != 0:
                    # print('cstrs: ', p, pa ,constrList)
                    qNo = 0
                    sumCost = 0
                    for cst in constrList:
                        cstr = cst[0]
                        matVals = cst[1]

                        matUtil = scopeConstrTable[cstr]
                        ut = matUtil[matVals[0]][matVals[1]]
                        if ut != '?':
                            sumCost = sumCost + int(ut)
                        else:
                            qNo = qNo +1

                leafCostDic[t] = (qNo, sumCost) #constrCostList
                sumList.append(sumCost)
                qNoList.append(qNo)

        #temp = sys.maxsize

        # for k in leafCostDic:
        #     (q, s) = leafCostDic[k]
        #     if temp > s and q == 0:
        #         temp = s
        #
        # minSum = temp
        #print(leafCostDic, max(qNoList), max(sumList))
        if len(qNoList)!=0:

            mqn = max(qNoList)
        else:
            mqn = 0

        if len(sumList)!=0:
            msum = max(sumList)
        else:
            msum = 0

        return leafCostDic, mqn, msum , leafNode #, minSum

    def updateCostAt_leaves(self, input,t,leavesAtMtrices, varList, treeNodeList, scopeConstrTable):
        # print 'treeeNODE:::: varList:::: ', len(treeNodeList), varList
        leafNode = varList[len(varList) - 1]
        # print(leafNode)
        leafCostDic = {}
        leafCostDic = copy.deepcopy(leavesAtMtrices)
        constrCostList = []
        # print(input.scopeConstrTable)
        maxC = 0
        maxQ = 0
        sumList = []
        qNoList = []

        for l in leavesAtMtrices:
            if t in l:
                k, p = treeNodeList[l].get_key_parent()
                #print('l: ', l, treeNodeList[l].get_key_parent())
                varVal = k.split('-')
                var = int(varVal[0])
                val = varVal[1]

                # print('k P: ', k, p)
                pList = p.split(';')

                pval = {}
                for i in pList:
                    vv = i.split('-')
                    pval[int(vv[0])] = vv[1]
                # key = k +':'+ p
                # constrCostList,qNo,sumCost = input.calculate_costAtLeaf(var, val, pval, scopeConstrTable)
                constrList = treeNodeList[l].get_relations()
                if len(constrList) != 0:
                    # print('cstrs: ', p, pa ,constrList)
                    qNo = 0
                    sumCost = 0
                    for cst in constrList:
                        cstr = cst[0]
                        matVals = cst[1]

                        matUtil = scopeConstrTable[cstr]
                        ut = matUtil[matVals[0]][matVals[1]]
                        if ut != '?':
                            sumCost = sumCost + int(ut)
                        else:
                            qNo = qNo + 1

                leafCostDic[l] = (qNo, sumCost)  # constrCostList
                sumList.append(sumCost)
                qNoList.append(qNo)

        # temp = sys.maxsize

        # for k in leafCostDic:
        #     (q, s) = leafCostDic[k]
        #     if temp > s and q == 0:
        #         temp = s
        #
        # minSum = temp
        # print(leafCostDic, max(qNoList), max(sumList))
        if len(qNoList) != 0:

            mqn = max(qNoList)
        else:
            mqn = 0

        if len(sumList) != 0:
            msum = max(sumList)
        else:
            msum = 0

        return leafCostDic, mqn, msum, leafNode  # , minSum


    def costAtNode(self, input,t, varList, treeNodeList, scopeConstrTable):

        #print 'treeeNODE:::: varList:::: ', len(treeNodeList), varList
        leafNode = varList[len(varList) - 1]
        #print(leafNode)
        leafCostDic = {}
        constrCostList = []
        #print(input.scopeConstrTable)
        maxC = 0
        maxQ = 0
        sumList = []
        qNoList = []

        if t in treeNodeList:
            k, p = treeNodeList[t].get_key_parent()

            varVal = k.split('-')
            var = int(varVal[0])
            val = varVal[1]

            if var == leafNode:
                #print('k P: ', k, p)
                pList = p.split(';')

                pval = {}
                for i in pList:
                    vv = i.split('-')
                    pval[int(vv[0])] = vv[1]
                #key = k +':'+ p
                #constrCostList,qNo,sumCost = input.calculate_costAtLeaf(var, val, pval, scopeConstrTable)
                constrList = treeNodeList[t].get_relations()
                if len(constrList) != 0:
                    # print('cstrs: ', p, pa ,constrList)
                    qNo = 0
                    sumCost = 0
                    for cst in constrList:
                        cstr = cst[0]
                        matVals = cst[1]

                        matUtil = scopeConstrTable[cstr]
                        ut = matUtil[matVals[0]][matVals[1]]
                        if ut != '?':
                            sumCost = sumCost + int(ut)
                        else:
                            qNo = qNo +1

                leafCostDic[t] = (qNo, sumCost) #constrCostList
                # sumList.append(sumCost)
                # qNoList.append(qNo)

        #temp = sys.maxsize

        # for k in leafCostDic:
        #     (q, s) = leafCostDic[k]
        #     if temp > s and q == 0:
        #         temp = s
        #
        # minSum = temp
        #print(leafCostDic, max(qNoList), max(sumList))
        return leafCostDic #, max(qNoList), max(sumList), leafNode #, minSum

    def leafCost_values(self,leafCostDic, leafNode, value):

        matDic = {}
        for k in leafCostDic:
            kp = k.split(':')
            leafval = kp[0].split('-')

            if leafval[0] == str(leafNode) and leafval[1] == str(value):
                matDic[k] = leafCostDic[k]

        return matDic

    def fillmatrix(self, matDic,nRows,nCols, divisor, coldivisor, maxSum):
        mat = np.zeros(shape=(nRows, nCols), dtype=int)
        #print "It is MAt DIC: ", matDic
        (qN,scost) = matDic
        matrixRanges = {}

        whichrow = round(float(scost /float (divisor)))
        #print ('whichrow and scost::: ',whichrow, scost, nRows, nCols)

        for i in range (0,int(nRows)):
            temp = []
            if i!=nRows-1:
                l = i*divisor
                u = (i+1) * divisor -1
                temp.append(l)
                temp.append(u)
            else:
                l = i * divisor
                u = l + divisor - 1
                temp.append(l)
                temp.append(u)

            matrixRanges[i] = temp



        if qN==0:
            q = 1
        else:
            q = qN
        #print 'whichrow and qNO here: ', whichrow, qN, nRows, nCols# , mat
        mat[whichrow][qN] = q

        return mat, matrixRanges

    def createMatrixLeafCost(self, maxqNo, maxSum, leafCostDic, leafNode, ldivisor, udivisor):
        fixConst = 40
        divisor = 1

        fixMaxQ = 10
        coldivisor = 1
        nMatrows = 0
        nMatCols = 0
        #print 'maxSum:', maxSum, maxqNo
        if maxSum < fixConst:
            divisor = ldivisor
            #print 'maxSum:', maxSum
            nMatrows = round((maxSum) / divisor) + 1
        else:
            divisor = udivisor
            nMatrows = int(round((maxSum) / divisor) + 1)

        #print('Here # of rows : ', nMatrows)

        if maxqNo < fixMaxQ:
            nMatCols = maxqNo + 1
        else:
            nMatCols = int(round(maxqNo / coldivisor) + 1)

        matrixList = {}
        matrixRanges = {}
        #print 'LEAAAAF: ', maxSum, maxqNo
        #print 'leafCostDic:::::::::::::', leafCostDic
        for k in leafCostDic:
            # kr = k.replace(';',':',1)
            # kp = kr.split(':')
            #leafval = kp[0].split('-')
            #print('k: ', k)
            costMatrix = np.zeros(shape=(nMatrows, nMatCols), dtype=int)
            costMatrix, matrixRanges = self.fillmatrix(leafCostDic[k], nMatrows, nMatCols, divisor, coldivisor, maxSum)
            matrixList[k] = costMatrix

        #print(matrixList, matrixRanges)
        return (matrixList, matrixRanges, nMatrows, nMatCols)

    
    def fillNodeMatrix(self, nodeCostList, maxQno, maxSum, rowRangeThr, colRangethr, ldivisor, udivisor):

        divisor = 1
        coldivisor = 1
        nMatrows = 0
        nMatCols = 0
        #   print ('maxSum:', maxSum, maxQno, rowRangeThr)
        if maxSum < rowRangeThr:
            divisor = ldivisor#5
            # print 'maxSum:', maxSum
            nMatrows = round((maxSum) / divisor) + 1
        else:
            divisor = udivisor#20#10
            nMatrows = int(round((maxSum) / divisor) + 1)
            # print 'Here: ', (maxSum+divisor) / divisor, round((maxSum+divisor) / divisor)

        if maxQno < colRangethr:
            nMatCols = maxQno + 1
        else:
            nMatCols = int(round(maxQno / coldivisor) + 1)

        mat = np.zeros(shape=(nMatrows, nMatCols), dtype=int)
        

        for nc in nodeCostList:
            (qN, scost) = nodeCostList[nc]
            
            whichrow = int(scost / (divisor))
            #mat[whichrow][qN] = 0 
            if qN == 0:
                q = 1
                #print 'NO QQQQQQQ: ', q
            else:
                q = qN
            mat[whichrow][qN] = mat[whichrow][qN]+ q

        matrixRanges = {}
        for i in range (0,int(nMatrows)):
            temp = []
            if i!=nMatrows-1:
                l = i*divisor
                u = (i+1) * divisor -1
                temp.append(l)
                temp.append(u)
            else:
                l = i * divisor
                u = l + divisor - 1
                temp.append(l)
                temp.append(u)

            matrixRanges[i] = temp

        #print 'whichrow and qNO here: ', whichrow, qN, nRows, nCols# , mat
        return mat, matrixRanges, divisor

    def nodeMatrixComputation(self,graph,currentNodeIndex,parentsValues, leavesCostDic, rowRangeThr, colRangethr,ldivisor, udivisor, maxQno, maxSum):


        matrixList = {}
        matrixListRange = {}
        rowDivisor = 1

        for d in graph[currentNodeIndex].domain:
            pkey = str(graph[currentNodeIndex].ID) + '-'+ str(d)
            #print 'pkey:::::: ', pkey, parentsValues
            if len(parentsValues)!= 0:
                matrixkey = pkey
                mk = []

                for p in parentsValues:
                    vv = p.split('-')
                    if str(graph[currentNodeIndex].ID)!= vv[0]:
                        mk.append(p)

                if pkey not in mk:
                    mk.append(pkey)

                for m in mk:
                    if m!=pkey:
                        matrixkey += ';' + m

                nodeCostList = {}
                qList = []
                sumList = []

                for l in leavesCostDic:
                    tmp = []
                    kp = l.split(':')
                    ps = kp[1].split(';')
                    tmp.append(kp[0])
                    tmp.extend(ps)

                    if set(mk).issubset(set(tmp)) or set(tmp).issubset(set(mk)):
                        #print ('matrixkey:::::', matrixkey, kp[1],l)
                        #print ((set(mk).issubset(set(ps))), mk, ps, tmp, parentsValues)

                        nodeCostList[l] = leavesCostDic[l]
                        qList.append(leavesCostDic[l][0])
                        sumList.append(leavesCostDic[l][1])

                #maxQno = max(qList)
                #maxSum = max(sumList)
                #print ('nodeCostList: ', nodeCostList)
                mat, matrixRange, divisor = self.fillNodeMatrix(nodeCostList, maxQno, maxSum, rowRangeThr, colRangethr, ldivisor, udivisor)
                matrixkey = matrixkey.replace(';',':',1)
                #print 'matrixkey:::: ', matrixkey
                matrixList[matrixkey] = mat
                matrixListRange[matrixkey] = matrixRange
                rowDivisor = divisor
            else:
                nodeCostList = {}
                qList = []
                sumList = []

                for l in leavesCostDic:
                    kp = l.split(':')
                    if pkey in kp[1]:

                        nodeCostList[l] = leavesCostDic[l]
                        qList.append(leavesCostDic[l][0])
                        sumList.append(leavesCostDic[l][1])

                #maxQno = max(qList)
                #maxSum = max(sumList)

                mat, matrixRange, divisor = self.fillNodeMatrix(nodeCostList, maxQno, maxSum, rowRangeThr, colRangethr,
                                                                ldivisor, udivisor)
                matrixkey = pkey + ':'
                matrixList[matrixkey] = mat
                matrixListRange[matrixkey] = matrixRange
                rowDivisor = divisor

        #print 'maxQ and and MAXSUM: ', maxQno, maxSum
        #print matrixList
        return matrixList, matrixListRange, rowDivisor


    def matrixPropagation(self, index, graph, leafMatrixList, treeList):
        #print(index)
        gn = graph[index]
        #print leafMatrixList
        graph[index].setCostMatrices(leafMatrixList)
        leafNodeCostMat = copy.deepcopy(leafMatrixList)

        while gn.prevNode != None:

            temp = {}
            for d in gn.prevNode.domain:
                pkey = str(gn.prevNode.ID) + '-' + str(d)

                matCostlist= self.sumMatrices(pkey, graph[index].costOfMatrices)
                for k in matCostlist:
                    temp[k] = matCostlist[k]
                    #print k

            gn = gn.prevNode
            index = index - 1
            #print id
            graph[index].setCostMatrices(temp)

    def sumMatrices(self,pkey, costOfMatrices):

        #sumMatrix = np.zeros(dtype=int)
        matCost = {}
        sumMatrix = np.zeros(shape=(10,10), dtype=int)
        #print ('Cost: ', costOfMatrices)
        for k in costOfMatrices:
            sumMatrix = np.empty(shape=costOfMatrices[k].shape, dtype=int)
            ########
            kk = k.replace(';',':',1)
            ########
            keyParent = kk.split(':')
            prs = keyParent[1].split(';')
            if pkey in prs:

                for k2 in costOfMatrices:
                    sumMatrix = np.empty(shape=costOfMatrices[k].shape, dtype=int)
                    ######
                    kk2 = k2.replace(';',':',1)
                    #######
                    kp = kk2.split(':')
                    if kp[1] == keyParent[1] and (k!=k2) and kp[0]!=keyParent[0]:
                        #costOfMatrices[k2].shape
                        #print "mat:   ", costOfMatrices[k2], costOfMatrices[k]
                        sumMatrix = costOfMatrices[k2] + costOfMatrices[k]
                        pr = ''
                        for p in prs:

                            if p!=pkey:
                                if pr!='':
                                    pr = pr +';'+p
                                else:
                                    pr = p

                        newkey = pkey+':'+ pr

                        matCost[newkey] = sumMatrix
        #print 'MATSUM: ', matCost
        return matCost


    def sumMatricesParentList(self, pkeyList, costOfMatrices):

        #sumMatrix = np.zeros(dtype=int)
        matCost = {}
        sumMatrix = np.zeros(shape=(10,10), dtype=int)
        for k in costOfMatrices:
            sumMatrix = np.empty(shape=costOfMatrices[k].shape, dtype=int)
            keyParent = k.split(':')
            prs = keyParent[1]
            #print pkeyList
            if prs == pkeyList:

                for k2 in costOfMatrices:
                    kp = k2.split(':')
                    if kp[1] == keyParent[1] and (k != k2) and kp[0] != keyParent[0]:

                        sumMatrix = costOfMatrices[k2] + costOfMatrices[k]

                        newkey = prs.replace(';',':',1)

                        matCost[newkey] = sumMatrix

        return matCost
        

    def findUBinMatrix(self, matRowRangeList, ub):
        for r in matRowRangeList:
            lu = matRowRangeList[r]
            l = int(lu[0])
            u = int(lu[1])

            if l <= ub and ub <= u:
                return r

    def matrixCostMaxCol(self, matrix, maxMissingcost, matRowRangeList, ub):
        totalMatCost = 0
        (nr, nc) = matrix.shape
        #print 'here: ', len(matRowRangeList), nr
        rowUB = -1
        if ub!= sys.maxsize:
            rowUB = self.findUBinMatrix(matRowRangeList, ub)

        if rowUB >= 0 and nr >= rowUB:
            #print 'We are HERE::::::', nr
            nr = rowUB + 1
            #print matrix
            #print 'We are HERE::::::', rowUB

        for r in range(0, nr):
            for c in range(0, nc):
                el = matrix[r][c]
                if el!=0:
                    lu = matRowRangeList[r]
                    u = int(lu[1])
                    cost = (el * u) + (el * c * maxMissingcost)
                    totalMatCost = totalMatCost + cost

        return totalMatCost

    def matrixCostMinCol(self, matrix, minMissingCost, matRowRangeList, ub):
        totalMatCost = 0
        (nr, nc) = matrix.shape
        rowUB = -1
        if ub != sys.maxsize:
            rowUB = self.findUBinMatrix(matRowRangeList, ub)

        if rowUB >= 0 and nr >= rowUB:
            #print 'We are HERE::::::', nr
            nr = rowUB + 1
            #print 'We are HERE::::::', rowUB

        for r in range(0, nr):
            for c in range(0, nc):
                el = matrix[r][c]
                if el!= 0:
                    lu = matRowRangeList[r]

                    u = int(lu[1])
                    cost = (el * u) + (el * c * minMissingCost)
                    totalMatCost = totalMatCost + cost

        return totalMatCost

    def matrixCostMinRowMinCol(self, matrix, minMissingCost, matRowRangeList, ub):
        totalMatCost = 0
        (nr, nc) = matrix.shape
        
        rowUB = -1
        if ub != sys.maxsize:
            rowUB = self.findUBinMatrix(matRowRangeList, ub)

        if rowUB >= 0 and nr >= rowUB:
            #print 'We are HERE::::::', nr
            nr = rowUB + 1
            #print 'We are HERE::::::', rowUB

        for r in range(0, nr):
            for c in range(0, nc):
                
                el = matrix[r][c]
                if str(el) != '':
                    lu = matRowRangeList[r]
                    l = int(lu[0])
                    cost = (el * l) + (el * c * minMissingCost)
                    #cost = (el * r) + (el * c * minMissingCost)
                    totalMatCost = totalMatCost + cost

        return totalMatCost

    def matrixCostMinRowMaxCol(self, matrix, maxMissingCost, matRowRangeList, ub):
        totalMatCost = 0
        (nr, nc) = matrix.shape

        rowUB = -1
        if ub != sys.maxsize:
            rowUB = self.findUBinMatrix(matRowRangeList, ub)

        if rowUB >= 0 and nr >= rowUB:
            #print 'We are HERE::::::', nr
            nr = rowUB + 1
            #print 'We are HERE::::::', rowUB

        for r in range(0, nr):
            for c in range(0, nc):
                el = matrix[r][c]
                if int(el) != 0:
                    lu = matRowRangeList[r]
                    l = int(lu[0])
                    cost = (el * l) + (el * c * maxMissingCost)
                    totalMatCost = totalMatCost + cost

        return totalMatCost


    def compareMatrices(self, matrixList):
        frobeniusNorm = {}
        # Frobenius Norm to compare the matrices

        for m in matrixList:
            mt = matrixList[m]
            frobeniusNorm[m] = LA.norm(mt, 'fro')

        print(frobeniusNorm)
        return(frobeniusNorm)

    def createGraph(self, input):
        variables = input.varList
        orderedVar = self.variableOrdering(variables)
        graphs = []

        domain = []
        prevNode = None
        nextNode = None

        neighbors = []
        chosenvalue = []

        for i in range(0,len(orderedVar)):

            domain = input.varDomainList[orderedVar[i]]
            gn = GraphNode(orderedVar[i], domain)
            graphs.append(gn)

        for j in range(0,len(graphs)):
            gn = graphs[j]
            prevNode = None if j == 0 else graphs[j - 1]
            gn.setprevNode(prevNode)
            nextNode = None if j == len(graphs) - 1 else graphs[j + 1]
            gn.setnextNode(nextNode)
            neighbors = input.adjancencyDic[orderedVar[gn.ID]]
            for n in neighbors:
                gn.addneighbors(n)

        return graphs

    def createMat(self, matDic,nRows,nCols, divisor, coldivisor):
        mat = np.zeros(shape=(nRows, nCols), dtype=int)
        #print "It is MAt DIC: ", matDic
        (qN,scost) = matDic
       
        #print 'scost::: ', scost, nRows
        whichrow = int(scost / (divisor))

        if qN ==0:
            q = 1
        else:
            q = qN
        #print 'whichrow and qNO here: ', whichrow, qN, nRows, nCols# , mat
        mat[whichrow][qN] = q

        return mat

    def getCost(self, input, varVal1,varVal2, scopeConstrTable):

        vv1 = varVal1.split('-')
        vv2 = varVal2.split('-')
        sc1 = vv1[0] + ' '+ vv2[0]
        sc2 = vv2[0] + ' '+ vv1[0]
        constr = ''
        constrvalues = []
        if sc1 in scopeConstrTable:
            costMat = scopeConstrTable[sc1]
            cost = costMat[int(vv1[1])-1][int(vv2[1])-1]
            constr = sc1
            constrvalues = (int(vv1[1])-1, int(vv2[1])-1)
        elif sc2 in scopeConstrTable:
            costMat = scopeConstrTable[sc2]
            cost = costMat[int(vv2[1])-1][int(vv1[1])-1]
            constr = sc2
            constrvalues = (int(vv2[1])-1 , int(vv1[1])-1)
        else:
            cost = None    

            
        return cost, constr, constrvalues

    def sumCost(self, parents, key, scopeConstrTable):
        sumCost = 0 
        questionN = 0
        parList = []
        constraints = []
        if re.search(';',parents):
            prs = parents.split(';')
            parList.extend(prs)
        else:
            parList.append(parents)


        for p in parList:
            c, constr,constrvalues = self.getCost(input, key,p, scopeConstrTable)
            
            if c!=None and c!='?':
                sumCost = sumCost + int(c)
            elif c!=None and c=='?':
                questionN = questionN +1
            else:
                sumCost = sumCost + 0
                questionN = questionN + 0        
            if constr!='':    
                constraints.append((constr,constrvalues))    
        
        return (questionN, sumCost, constraints)        

    def matrixAtNode(self, nodeID,pr, treeNodeList, lowerLevelMatrices, nRows,nCols, divisor, coldivisor):

        #print 'treeeNODE:::: varList:::: ', len(treeNodeList), varList
        
        #print(leafNode)
        leafCostDic = {}
        constrCostList = []
        #print(input.scopeConstrTable)
        maxC = 0
        maxQ = 0
        sumList = []
        qNoList = []
        nodeMatrices = {}
        for t in treeNodeList:
            if pr in t:
                k, p = treeNodeList[t].get_key_parent()
                cumulativeMat = np.zeros(shape=(nRows, nCols), dtype=int)
                varVal = k.split('-')
                var = varVal[0]

                if p != None and p != '':
                    key = k+';'+p
                else:
                    key = k

                listOfmat = []

                if var == nodeID:
                    children = treeNodeList[t].get_children()
                    #print('Children: ',t, treeNodeList[t].get_children() )
                    for c in children:
                        #qn, sc = treeNodeList[c].get_value()
                        matrix = lowerLevelMatrices[c] #self.createMat((qn, sc),nRows,nCols, divisor, coldivisor)
                        listOfmat.append(matrix)

                    for l in listOfmat:
                        cumulativeMat = cumulativeMat + l

                    nodeMatrices[key] =  cumulativeMat
         
        #print(nodeMatrices)
        return  nodeMatrices#, minSum

    def solutionlistAtNode(self, graph, indexID, parents, domain,  treeNodeList, leavesSolutions, lowerBoundCost):
        unknownatNodes = {}

        # for i in range(0,len(graph)):
        #     nodeID = str(graph[i].ID)
        #
        #     for t in treeNodeList:
        #         k, p = treeNodeList[t].get_key_parent()
        #
        #         varVal = k.split('-')
        #         var = varVal[0]
        #
        #         if p != None and p != '':
        #             key = k + ';' + p
        #         else:
        #             key = k
        #
        #         solList = []
        #         if var == nodeID:
        #             for l in leavesSolutions:
        #                 if t in l:
        #                     solList.append(l)
        #
        #             unknownatNodes[key] = solList

        for d in domain:
            key = str(indexID)+'-'+str(d)
            if parents != '':
                path = key + ';' + parents
            else:
                path = key

            solList = []
            for l in leavesSolutions:
                if path in l:
                    solList.append(l)
            unknownatNodes[path] = solList

        unknownCosts = {}
        for u in unknownatNodes:
            lst = unknownatNodes[u]
            lstCost = []
            for l in lst:
                q, s = leavesSolutions[l]
                lstCost.append((q, s, l))
            unknownCosts[u] = lstCost
        #print('unknownatNodes, and unknownCosts:::: ', unknownatNodes, unknownCosts)
        return unknownatNodes, unknownCosts

    # def solutionlistAtNode(self, graph, treeNodeList, leavesSolutions, lowerBoundCost):
    #     unknownatNodes = {}
    #
    #     for i in range(0,len(graph)):
    #         nodeID = str(graph[i].ID)
    #
    #         for t in treeNodeList:
    #             k, p = treeNodeList[t].get_key_parent()
    #
    #             varVal = k.split('-')
    #             var = varVal[0]
    #
    #             if p != None and p != '':
    #                 key = k + ';' + p
    #             else:
    #                 key = k
    #
    #             solList = []
    #             if var == nodeID:
    #                 for l in leavesSolutions:
    #                     if t in l:
    #                         solList.append(l)
    #
    #                 unknownatNodes[key] = solList
    #
    #     unknownCosts = {}
    #     for u in unknownatNodes:
    #         lst = unknownatNodes[u]
    #         lstCost = []
    #         for l in lst:
    #             q, s = leavesSolutions[l]
    #             lstCost.append((q, s, l))
    #         unknownCosts[u] = lstCost
    #
    #     return unknownatNodes, unknownCosts


    def missingAtNode(self, nodeID, treeNodeList, lowerLevelUnknownCosts, lowerBoundCost):

        # print 'treeeNODE:::: varList:::: ', len(treeNodeList), varList

        # print(leafNode)
        leafCostDic = {}
        constrCostList = []
        # print(input.scopeConstrTable)
        maxC = 0
        maxQ = 0
        sumList = []
        qNoList = []
        unknownatNodes = {}
        for t in treeNodeList:
            k, p = treeNodeList[t].get_key_parent()

            varVal = k.split('-')
            var = varVal[0]

            if p != None and p != '':
                key = k + ';' + p
            else:
                key = k

            listOfmissing = {}

            if var == nodeID:
                children = treeNodeList[t].get_children()
                # print('Children: ',t, treeNodeList[t].get_children() )
                for c in children:
                    # qn, sc = treeNodeList[c].get_value()
                    #print('lowerLevelUnknownCosts: ', lowerLevelUnknownCosts)
                    (q, s, branch) = lowerLevelUnknownCosts[c]  # self.createMat((qn, sc),nRows,nCols, divisor, coldivisor)
                    #print ('C : ', c, q, s, branch)
                    listOfmissing[c] = (q, s, branch)

                minSumQ = sys.maxsize
                minQ = 0
                minQSum = 0
                minBranch = ''
                for u in listOfmissing:
                    (mq, ms, b) = listOfmissing[u]
                    su = mq #ms + mq * lowerBoundCost
                    if minSumQ > su:
                        minSumQ = su
                        minQ = mq
                        minQSum = ms
                        minBranch = b

                #print('min: ', minQ)
                unknownatNodes[key] = (minQ, minQSum, minBranch)

        return unknownatNodes  # , minSum

    def treeGen(self, graphs, gt, node,scopeConstrTable):
        gr = copy.deepcopy(graphs)

        parent = None
        value = None
        
        treeNodeList = {} #[]
        stackParents = []
        for n in gr:

            if n.prevNode == None:

                for d in n.domain:
                    key = (str(n.ID) + '-' + str(d))
                    value = (0,0)
                    tu = gt.generate_node(key, value, parent)

                    #treeNodeList.append(tu)
                    treeNodeList[key] = tu
                    if parent == None:
                        k = key
                    stackParents.append(k)

            else:
                auxstack = []
                while len(stackParents) != 0:
                    parent = stackParents.pop()
                    (prevQN, prevsumC) = (0,0)
                    chl = []
                    

                    if parent in treeNodeList:
                        nt = treeNodeList[parent]        
                        (prevQN, prevsumC) = nt.get_value()

                        pcs = nt.get_relations()
                        #print('PCS relation: ', pcs)
                    for d in n.domain:
                        constrs = []
                        if parent in treeNodeList:
                            constrs.extend(pcs)

                        key = (str(n.ID) + '-' + str(d))
                        #print('here: ',key, parent)
                        (qN,sumC, contrList) = gt.sumCost(parent, key, scopeConstrTable)
                        value = (qN+prevQN,sumC+prevsumC)
                        
                        tu = gt.generate_node(key, value, parent)

                        #treeNodeList.append(tu)
                        # if key not in auxstack:
                        k = key + ';' + parent
                        
                        chl.append(k)
                        #print('contrList', constrs)

                        for c in contrList:
                            if c[0]!='' and c[0] not in constrs:
                                constrs.append(c)
                        #print('key par: ', key,parent, value, (prevQN, prevsumC))
                        treeNodeList[k] = tu

                        auxstack.append(k)
                        #print('k, constr: ', k , constrs)
                        
                        tu.add_relation(constrs) 
                                             
                    nt.add_child(chl) 

                stackParents = auxstack

        
        return treeNodeList



    def variableOrdering(self, varList):
        orderedList = []
        orderedList = sorted(varList, reverse=True)
        return orderedList

def main():
    path = ""

    xmlfile = open(argv[1], 'r')
    

    weight = float(argv[2])
    

    divisor = int(argv[3])
    if divisor==0:
        divisor= 50
    
    method = str(argv[4])

    suboptimal = str(argv[5])

    elicitCost = int(argv[6])

    path = str(argv[7])
    name = str(argv[8])

    # path = "/home/cdao/Atena/aaai2019/optimal/cop-ISBB/"
    incomp = open(path + 'output-Incomp'+'-'+name+'.txt', 'r')
    oracle = open(path + 'oracle'+'-'+name+'.txt', 'r')
    elicit = open(path + 'elicit'+'-'+name+'.txt', 'r')
    #print(elicit)
    input = readInput.ReadInput(xmlfile, path, name)

    sys.setrecursionlimit(50100)
    ###read input xml file as the given problem
    if suboptimal == 'a':
        if weight <= 1:
            weight = 0
        #print('weight: ', weight)    
    else:
        if weight < 1:
            weight = 1        

    ###ordering of the variables in the problem
    varList = (sorted(input.varList, reverse=True))
    domainrange = input.nvalues

    incompTable, variables, varDomain = input.readIncomp(incomp)
    oracleTable = input.readOracle(oracle, domainrange)

    elicitationTable = input.readElicitationCost(elicit, domainrange)

    #print("elicitationTable", elicitationTable)
    #print(incompTable)
    lbc = min(input.allcostList)
    ubc = max(input.allcostList)
    
    start = time.time()
    ct = time.time()
    gt = GenerateTree()

    graphs = gt.createGraph(input)
    generatedTree = gt.treeGen(graphs, gt, graphs[0], incompTable)
    cte = time.time()
    #gt.costAt_leaves(input, varList, generatedTree, incompTable)
    
    #print('Runtime to construct the treee: ', (cte-ct))

    sbb = SynchBB(graphs, generatedTree,lbc,ubc, weight, divisor,method, suboptimal, elicitCost)

    sbb.synch_iterative(input, gt,varList, incompTable, oracleTable, elicitationTable)
    end = time.time()
    runtime = end - start
    
    #print(oracleTable)
    #print(sbb.incompTable)
    #print(elicitationTable)
    print (str(lbc)+','+str(ubc)+',' + str(sbb.ub)+','+ str(sbb.actualConstraintCost)+','+
           str(sbb.actualElicitedCostSofar)+ ','+str(sbb.elicitationNum) +','+str(input.maxQ)+','+str(runtime)+','+str(sbb.optSol_elicitationCost))
    print (sbb.completeAsg)
    


if __name__ == '__main__':
    main()
