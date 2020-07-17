import random
import time
from itertools import combinations

import readInput
from LocalSearchProblem import LocalSearchProblem


class LocalSearch_IWCSP(LocalSearchProblem):
    #name: filename
    def __init__(self, name, tabu_list_maxsize, heuristic = None, elicitation_strat = 'ALL'):
        path = './'
        xmlfile = 'input_files/Rnd5-3-1.xml'
        incomp = open(path + 'output-Incomp'+'-'+name+'.txt', 'r')
        oracle = open(path + 'oracle'+'-'+name+'.txt', 'r')
        elicit = open(path + 'elicit'+'-'+name+'.txt', 'r')
        self.input = readInput.ReadInput(xmlfile, path, name)
        self.varList = (sorted(self.input.varList, reverse=True))
        self.domainrange = self.input.nvalues
        self.incompTable, variables, varDomain = self.input.readIncomp(incomp)
        self.oracleTable = self.input.readOracle(oracle, self.domainrange)
        self.elicitationTable = self.input.readElicitationCost(elicit, self.domainrange)
        self.lbc = min(self.input.allcostList)
        self.elicitation_number = 0
        self.elicitation_cost = 0
        self.elicitation_strat = elicitation_strat
        self.tabu_list = []
        self.tabu_list_maxsize = tabu_list_maxsize
        self.heuristic = heuristic
        self.best_val = float('inf')
        self.current_assign = self.get_starting_assign()



    #choose random starting assignment
    def get_starting_assign(self):
        starting_dict = {key: random.randint(1, self.domainrange) for key in self.varList}
        scopes = self.incompTable.keys()
        answer_list = list(starting_dict)
        comb = [(str(x) + ' ' +  str(y)) for idx, x in enumerate(answer_list) for y in answer_list[idx + 1: ]]
        #iterate through constraints and update the incomplete table with elicited values
        for scope in comb:
            if scope in self.incompTable or scope[::-1] in self.incompTable:
                if scope[::-1] in self.incompTable:
                    scope = scope[::-1]
                scope_values = [int(i) for i in scope.split()]
                row_cell = starting_dict[scope_values[0]] - 1
                column_cell = starting_dict[scope_values[1]] - 1

                if self.incompTable[scope][row_cell][column_cell] == '?':
                    elicited_value = self.oracleTable[scope][row_cell][column_cell]
                    self.incompTable[scope][row_cell][column_cell] = elicited_value
                    elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                    self.elicitation_cost += int(elicitation_cost)
                    self.elicitation_number += 1

        self.best_val = self.compute_preference(starting_dict)[0]
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
                row_cell = self.current_assign[scope_values[0]] - 1
                column_cell = self.current_assign[scope_values[1]] - 1

                if self.incompTable[scope][row_cell][column_cell] == '?':
                    constraint_value = 0
                    if self.heuristic == 'lbc':
                        constraint_value = self.lbc
                else:
                    constraint_value = self.incompTable[scope][row_cell][column_cell]

                local_pref_dict[scope_values[0]].append(int(constraint_value))
                local_pref_dict[scope_values[1]].append(int(constraint_value))

        best_variable = None
        max_val = float('-inf')

        for vars in self.tabu_list:
            if vars in local_pref_dict:
                del local_pref_dict[vars]

        for key in local_pref_dict:
            if sum(local_pref_dict[key]) > max_val:
                best_variable = key
                max_val = sum(local_pref_dict[key])

        return best_variable


    #chooses value for variable that should be updated in local search
    def choose_value_for_variable(self, variable):

        if (variable is None):
            return

        old_value = self.current_assign[variable]
        preferences = {}

        for value in range(1,self.domainrange+1):
            if value != old_value:
                new_assign = self.current_assign.copy()
                new_assign[variable] = value
                preferences[value] = self.compute_preference(new_assign)

        #we want the value that minimizes the cost
        best_value = None
        min = float('inf')

        for value in preferences:
            if preferences[value][0] < min:
                best_value = value
                min = preferences[value][0]
            elif (preferences[value][0] == min):
                if (preferences[value][1] < preferences[best_value][1]):
                    best_value = value
                    min = preferences[value][0]

        return best_value

    #computes the preference of a given assignment
    def compute_preference(self, assignment, elicit = False):
        scopes = self.incompTable.keys()
        answer_list = list(assignment)
        comb = [(str(x) + ' ' +  str(y)) for idx, x in enumerate(answer_list) for y in answer_list[idx + 1: ]]
        preference_val = 0
        count = 0
        elicit_list = []
        elicit_dict = {}
        for scope in comb:
            if scope in self.incompTable or scope[::-1] in self.incompTable:
                if scope[::-1] in self.incompTable:
                    scope = scope[::-1]
                scope_values = [int(i) for i in scope.split()]

                row_cell = assignment[scope_values[0]] - 1
                column_cell = assignment[scope_values[1]] - 1

                if (elicit):
                    if self.elicitation_strat == 'ALL':
                        if self.incompTable[scope][row_cell][column_cell] == '?':
                            elicited_value = self.oracleTable[scope][row_cell][column_cell]
                            self.incompTable[scope][row_cell][column_cell] = elicited_value
                            elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                            self.elicitation_cost += int(elicitation_cost)
                            self.elicitation_number += 1
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value
                    if self.elicitation_strat == "WW":
                        if self.incompTable[scope][row_cell][column_cell] == '?':
                            elicited_value = self.oracleTable[scope][row_cell][column_cell]
                            elicit_list.append(int(elicited_value))
                            elicit_dict[int(elicited_value)] = [scope, row_cell, column_cell]
                        else:
                            constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                            preference_val += constraint_value
                else:
                    if self.incompTable[scope][row_cell][column_cell] != '?':
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value
                    else:
                        if self.heuristic == 'lbc':
                            preference_val += self.lbc
                        count += 1

        if (elicit and self.elicitation_strat == "WW"):
            elicit_list.sort(reverse = True)
            # print ('PrefValBefore: ' + str(preference_val))
            # print (elicit_list)
            index = 0
            while ((preference_val < self.best_val) and (index < len(elicit_list))):
                val = elicit_list[index]
                scope = elicit_dict[val][0]
                row_cell = elicit_dict[val][1]
                column_cell = elicit_dict[val][2]
                self.incompTable[scope][row_cell][column_cell] = val
                elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                self.elicitation_cost += int(elicitation_cost)
                self.elicitation_number += 1
                constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                preference_val += constraint_value
                index += 1
            #print ('PrefVal: ' + str(preference_val))



        return ([preference_val, count])

    #updates assignment
    def update_assign(self, variable, value):
        new_assign = self.current_assign.copy()
        new_assign[variable] = value

        if (variable is None):
            self.tabu_list.append(variable)
            if (len(self.tabu_list) > self.tabu_list_maxsize):
                self.tabu_list.pop(0)
            return

        new_val = self.compute_preference(new_assign, elicit = True)[0]

        #compares two lists using lexigraphical ordering
        if new_val < self.best_val:
            #print ("changed variable!")
            self.current_assign[variable] = value
            self.best_val = new_val
        else:
            if variable not in self.tabu_list:
                #print ("added tabu")
                self.tabu_list.append(variable)
            if (len(self.tabu_list) > self.tabu_list_maxsize):
                self.tabu_list.pop(0)

    def solve(self, iterations = 0, p = 0.00):
        for i in range(0, iterations):
            random_step_chance = random.random()
            if (random_step_chance > p):
                var = self.choose_variable()
            else:
                var = random.choice(self.varList)
            value = self.choose_value_for_variable(var)
            self.update_assign(var, value)

        return self.current_assign

preferences = []
runtimes = []
elicitation_cost = []
elicitation_numbers = []


for i in range(0,10):

    start = time.time()
    LSP = LocalSearch_IWCSP('1', 1000, elicitation_strat = 'WW')
    # print (LSP.current_assign)
    # print (LSP.best_val)
    LSP.solve(iterations = 100000, p = 0.20)
    end = time.time()
    runtime = end - start
    preferences.append(LSP.compute_preference(LSP.current_assign)[0])
    runtimes.append(runtime)
    elicitation_cost.append(LSP.elicitation_cost)
    print (LSP.elicitation_cost)
    elicitation_numbers.append(LSP.elicitation_number)

    # print (LSP.current_assign)
    # print (LSP.compute_preference(LSP.current_assign))
    # print (runtime)
    # print (LSP.elicitation_number)

print (sum(preferences)/ len(preferences))
print (sum(runtimes)/ len(runtimes))
print (sum(elicitation_cost)/ len(elicitation_cost))
print (sum(elicitation_numbers)/ len(elicitation_numbers))
print (LSP.current_assign)
