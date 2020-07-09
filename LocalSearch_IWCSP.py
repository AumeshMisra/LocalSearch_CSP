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
        scopes = self.incompTable.keys()
        answer_list = list(starting_dict)
        comb = [(str(x) + ' ' +  str(y)) for idx, x in enumerate(answer_list) for y in answer_list[idx + 1: ]]
        #iterate through constraints and update the incomplete table with elicited values
        for scope in comb:
            if scope in self.incompTable or scope[::-1] in self.incompTable:
                if scope[::-1] in self.incompTable:
                    scope = scope[::-1]
                scope_values = [int(i) for i in scope.split()]
                row_cell = starting_dict[scope_values[0]]
                column_cell = starting_dict[scope_values[1]]

                if self.incompTable[scope][row_cell][column_cell] == '?':
                    elicited_value = self.oracleTable[scope][row_cell][column_cell]
                    self.incompTable[scope][row_cell][column_cell] = elicited_value

        return starting_dict


    #chooses variable that should be updated in local search
    def choose_variable(self):
        local_pref_dict = {key: [] for key in self.varList}
        scopes = self.incompTable.keys()
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

        best_variable = 0
        max_val = float('-inf')

        for key in local_pref_dict:
            if sum(local_pref_dict[key]) > max_val:
                best_variable = key
                max_val = sum(local_pref_dict[key])

        return best_variable


    #chooses value for variable that should be updated in local search
    def choose_value_for_variable(self, variable):
        old_value = self.current_assign[variable]
        preferences = {}
        for value in range(0,self.domainrange):
            if value != old_value:
                new_assign = self.current_assign.copy()
                new_assign[variable] = value
                preferences[value] = self.compute_preference(new_assign)

        #we want the value that minimizes the cost
        best_value = min(preferences, key=preferences.get)
        return best_value

    #computes the preference of a given assignment
    def compute_preference(self, assignment, elicit = False):
        scopes = self.incompTable.keys()
        answer_list = list(assignment)
        comb = [(str(x) + ' ' +  str(y)) for idx, x in enumerate(answer_list) for y in answer_list[idx + 1: ]]
        preference_val = 0
        for scope in comb:
            if scope in self.incompTable or scope[::-1] in self.incompTable:
                if scope[::-1] in self.incompTable:
                    scope = scope[::-1]
                scope_values = [int(i) for i in scope.split()]

                row_cell = assignment[scope_values[0]]
                column_cell = assignment[scope_values[1]]

                if (elicit):
                    if self.incompTable[scope][row_cell][column_cell] == '?':
                        elicited_value = self.oracleTable[scope][row_cell][column_cell]
                        self.incompTable[scope][row_cell][column_cell] = elicited_value
                    constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                    preference_val += constraint_value
                else:
                    if self.incompTable[scope][row_cell][column_cell] != '?':
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value

        return preference_val

    #updates assignment
    def update_assign(self, variable, value):
        new_assign = self.current_assign.copy()
        new_assign[variable] = value

        if self.compute_preference(new_assign, elicit = True) < self.compute_preference(self.current_assign):
            print ("changed variable!")
            self.current_assign[variable] = value
            print (self.current_assign)

    def solve(self, iterations = 100, p = 0.00):
        for i in range(0, iterations):
            random_step_chance = random.random()
            if (random_step_chance > p):
                var = self.choose_variable()
            else:
                var = random.choice(self.varList)
            value = self.choose_value_for_variable(var)
            self.update_assign(var, value)


        print (self.current_assign)
        print (self.compute_preference(self.current_assign))
        return self.current_assign

LSP = LocalSearch_IWCSP('1')
#print(LSP.current_assign)
# var = LSP.choose_variable()
# #print('var: ' + str(var))
# value = LSP.choose_value_for_variable(var)
# LSP.update_assign(var, value)
# #print (LSP.current_assign)
# LSP.choose_variable()
#print (LSP.varList)
print (LSP.current_assign)
LSP.solve(iterations = 1000, p = 0.20)
