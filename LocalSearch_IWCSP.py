import random
from itertools import combinations

import readInput
from LocalSearchProblem import LocalSearchProblem


class LocalSearch_IWCSP(LocalSearchProblem):
    #name: filename
    def __init__(self, name):
        path = './'
        xmlfile = 'input_files/Rnd3-2.xml'
        incomp = open(path + 'output-Incomp'+'-'+name+'.txt', 'r')
        oracle = open(path + 'oracle'+'-'+name+'.txt', 'r')
        elicit = open(path + 'elicit'+'-'+name+'.txt', 'r')
        self.input = readInput.ReadInput(xmlfile, path, name)
        self.varList = (sorted(self.input.varList, reverse=True))
        self.domainrange = self.input.nvalues
        self.incompTable, variables, varDomain = self.input.readIncomp(incomp)
        self.oracleTable = self.input.readOracle(oracle, self.domainrange)
        self.elicitationTable = self.input.readElicitationCost(elicit, self.domainrange)
        self.current_assign = self.get_starting_assign()

    #choose random starting assignment
    def get_starting_assign(self):
        starting_dict = {key: random.randint(0, self.domainrange-1) for key in self.varList}
        return starting_dict


    #chooses variable that should be updated in local search
    def choose_variable(self):
        local_pref_dict = {key: [] for key in self.varList}
        scopes = self.incompTable.keys()
        print (self.current_assign)
        print (self.incompTable)
        answer_list = list(self.current_assign)
        comb = [(str(x) + ' ' +  str(y)) for idx, x in enumerate(answer_list) for y in answer_list[idx + 1: ]]
        for scope in comb:
            if scope in self.incompTable or scope[::-1] in self.incompTable:
                if scope[::-1] in self.incompTable:
                    scope = scope[::-1]
                scope_values = [int(i) for i in scope.split()]
                row_cell = self.current_assign[scope_values[0]]
                column_cell = self.current_assign[scope_values[1]]

                if self.incompTable[scope][row_cell][column_cell] == '?':
                    constraint_value = 0
                else:
                    constraint_value = self.incompTable[scope][row_cell][column_cell]

                local_pref_dict[scope_values[0]].append(int(constraint_value))
                local_pref_dict[scope_values[1]].append(int(constraint_value))

        print (local_pref_dict)
        best_variable = 0
        max_val = float('-inf')

        for key in local_pref_dict:
            if max(local_pref_dict[key]) > max_val:
                best_variable = key
                max_val = max(local_pref_dict[key])
                
        return best_variable


    #chooses value for variable that should be updated in local search
    def choose_value_for_variable(self, variable):
        pass


LSP = LocalSearch_IWCSP('1')
#print (LSP.input, LSP.varList, LSP.domainrange, LSP.incompTable, LSP.starting_assign)
#LSP.choose_variable()
LSP.choose_variable()
