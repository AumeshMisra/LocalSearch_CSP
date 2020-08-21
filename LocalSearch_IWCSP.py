import random
import time
from itertools import combinations
import numpy as np
import argparse

import readInput
from LocalSearchProblem import LocalSearchProblem


class LocalSearch_IWCSP(LocalSearchProblem):
    #name: filename
    def __init__(self, name, file_path, tabu_list_maxsize, budget, heuristic = None, elicitation_strat = 'ALL'):
        path = './'
        xmlfile = file_path
        incomp = open(path + 'output-Incomp'+'-'+name+'.txt', 'r')
        oracle = open(path + 'oracle'+'-'+name+'.txt', 'r')
        elicit = open(path + 'elicit'+'-'+name+'.txt', 'r')
        self.input = readInput.ReadInput(xmlfile, path, name)
        self.varList = (sorted(self.input.varList, reverse=True))
        self.domainrange = self.input.nvalues
        self.incompTable, variables, varDomain = self.input.readIncomp(incomp)
        self.oracleTable = self.input.readOracle(oracle, self.domainrange)
        self.elicitationTable = self.input.readElicitationCost(elicit, self.domainrange)
        self.budget = budget
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

        #array, dict for elicit constraint values
        elicit_value_list = []
        elicit_dict_value = {}

        #array, dict for elicit cost values
        elicit_cost_list = []
        elicit_dict_cost = {}

        for scope in comb:
            if scope in self.incompTable or scope[::-1] in self.incompTable:
                if scope[::-1] in self.incompTable:
                    scope = scope[::-1]
                scope_values = [int(i) for i in scope.split()]

                row_cell = assignment[scope_values[0]] - 1
                column_cell = assignment[scope_values[1]] - 1

                if (elicit):
                    if self.incompTable[scope][row_cell][column_cell] == '?':
                        #elicited values from oracle table
                        elicited_value = self.oracleTable[scope][row_cell][column_cell]
                        elicit_value_list.append(int(elicited_value))
                        elicit_dict_value[len(elicit_value_list)-1] = [scope, row_cell, column_cell]

                        #elicited costs
                        elicited_cost = self.elicitationTable[scope][row_cell][column_cell]
                        elicit_cost_list.append(int(elicited_cost))
                        elicit_dict_cost[len(elicit_cost_list)-1] = [scope, row_cell, column_cell]


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


        if (elicit):
            if (self.elicitation_cost + sum(elicit_cost_list)) < self.budget:
                #We elicit all missing values
                if (self.elicitation_strat == "ALL"):
                    index = 0
                    while ((index < len(elicit_value_list))):
                        scope = elicit_dict_cost[index][0]
                        row_cell = elicit_dict_cost[index][1]
                        column_cell = elicit_dict_cost[index][2]

                        #get elicitation cost
                        elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                        self.elicitation_cost += int(elicitation_cost)

                        #get elicitated value
                        self.incompTable[scope][row_cell][column_cell] = self.oracleTable[scope][row_cell][column_cell]
                        self.elicitation_number += 1
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value
                        index += 1

                #We only elicit until we either have an optimal assignment, or the assignment turns out to be worse
                if (self.elicitation_strat == "WW"):
                    sorted_indices = np.argsort(elicit_value_list)[::-1]
                    index = 0
                    while ((preference_val < self.best_val) and (index < len(sorted_indices))):
                        val = sorted_indices[index]
                        scope = elicit_dict_value[val][0]
                        row_cell = elicit_dict_value[val][1]
                        column_cell = elicit_dict_value[val][2]

                        #get elicitation cost
                        elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                        self.elicitation_cost += int(elicitation_cost)

                        #get elicitated value
                        self.incompTable[scope][row_cell][column_cell] = self.oracleTable[scope][row_cell][column_cell]
                        self.elicitation_number += 1
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value
                        index += 1
                if (self.elicitation_strat == "BB"):
                    sorted_indices = np.argsort(elicit_value_list)
                    index = 0
                    while ((preference_val < self.best_val) and (index < len(sorted_indices))):
                        val = sorted_indices[index]
                        scope = elicit_dict_value[val][0]
                        row_cell = elicit_dict_value[val][1]
                        column_cell = elicit_dict_value[val][2]

                        #get elicitation cost
                        elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                        self.elicitation_cost += int(elicitation_cost)

                        #get elicitated value
                        self.incompTable[scope][row_cell][column_cell] = self.oracleTable[scope][row_cell][column_cell]
                        self.elicitation_number += 1
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value
                        index += 1
                if (self.elicitation_strat == "BM"):
                    elicit_combined_list = [elicit_value_list[i]+elicit_cost_list[i] for i in range(len(elicit_value_list))]
                    sorted_indices = np.argsort(elicit_combined_list)
                    index = 0
                    while ((preference_val < self.best_val) and (index < len(sorted_indices))):
                        val = sorted_indices[index]
                        scope = elicit_dict_value[val][0]
                        row_cell = elicit_dict_value[val][1]
                        column_cell = elicit_dict_value[val][2]

                        #get elicitation cost
                        elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                        self.elicitation_cost += int(elicitation_cost)

                        #get elicitated value
                        self.incompTable[scope][row_cell][column_cell] = self.oracleTable[scope][row_cell][column_cell]
                        self.elicitation_number += 1
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value
                        index += 1
                if (self.elicitation_strat == "MM"):
                    sorted_indices = np.argsort(elicit_cost_list)
                    index = 0
                    while ((preference_val < self.best_val) and (index < len(sorted_indices))):
                        val = sorted_indices[index]
                        scope = elicit_dict_value[val][0]
                        row_cell = elicit_dict_value[val][1]
                        column_cell = elicit_dict_value[val][2]

                        #get elicitation cost
                        elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                        self.elicitation_cost += int(elicitation_cost)

                        #get elicitated value
                        self.incompTable[scope][row_cell][column_cell] = self.oracleTable[scope][row_cell][column_cell]
                        self.elicitation_number += 1
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value
                        index += 1
                if (self.elicitation_strat == "WM"):
                    elicit_combined_list = [elicit_value_list[i]+elicit_cost_list[i] for i in range(len(elicit_value_list))]
                    sorted_indices = np.argsort(elicit_combined_list)
                    sorted_indices = sorted_indices[::-1]
                    index = 0
                    while ((preference_val < self.best_val) and (index < len(sorted_indices))):
                        val = sorted_indices[index]
                        scope = elicit_dict_value[val][0]
                        row_cell = elicit_dict_value[val][1]
                        column_cell = elicit_dict_value[val][2]

                        #get elicitation cost
                        elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                        self.elicitation_cost += int(elicitation_cost)

                        #get elicitated value
                        self.incompTable[scope][row_cell][column_cell] = self.oracleTable[scope][row_cell][column_cell]
                        self.elicitation_number += 1
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value
                        index += 1
                if (self.elicitation_strat == "BW"):
                    elicit_combined_list = [elicit_value_list[i]+elicit_cost_list[i] for i in range(len(elicit_value_list))]
                    sorted_indices = np.argsort(elicit_combined_list)
                    first = 0
                    switch = 0
                    last = len(sorted_indices) - 1
                    while ((preference_val < self.best_val) and (first <= last)):
                        if ((switch % 2) == 0):
                            index = first
                            first += 1
                        else:
                            index = last
                            last -= 1
                        val = sorted_indices[index]
                        scope = elicit_dict_value[val][0]
                        row_cell = elicit_dict_value[val][1]
                        column_cell = elicit_dict_value[val][2]

                        #get elicitation cost
                        elicitation_cost = self.elicitationTable[scope][row_cell][column_cell]
                        self.elicitation_cost += int(elicitation_cost)

                        #get elicitated value
                        self.incompTable[scope][row_cell][column_cell] = self.oracleTable[scope][row_cell][column_cell]
                        self.elicitation_number += 1
                        constraint_value = int(self.incompTable[scope][row_cell][column_cell])
                        preference_val += constraint_value

            else:
                #right now return this however we should come up with a new elicitation strategy
                return([float('inf'), 0])




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
            if (self.elicitation_cost > self.budget):
                break
            random_step_chance = random.random()
            if (random_step_chance > p):
                var = self.choose_variable()
            else:
                var = random.choice(self.varList)
            value = self.choose_value_for_variable(var)
            self.update_assign(var, value)

        return self.current_assign

def define_parser():
    parser = argparse.ArgumentParser(description='Process Arguments For Local Search.')
    parser.add_argument('--iterations', type=int,
                        help='an integer for the number of iterations')
    parser.add_argument('--budget', type=int,
                        help='an integer for the budget')
    parser.add_argument('--flag', type=int,
                        help='a flag to use elicitation cost')
    parser.add_argument('--original', type=int,
                        help='a flag to go back to the original proble. We can only use BB, WW, and ALL elicitation strategies')
    parser.add_argument('--strategy', type=str,
                        help='an elicitation strategy to use')
    parser.add_argument('--filepath', type=str,
                        help='the filepath to a problem')
    return (parser)

def main():
    preferences = []
    runtimes = []
    elicitation_cost = []
    elicitation_numbers = []

    parser = define_parser()
    args = parser.parse_args()

    iterations = args.iterations
    elicitation_strat = args.strategy
    filepath = args.filepath
    if (args.flag == 1):
        budget = args.budget
    else:
        budget = float('inf')

    if (args.original == 1):
        if (elicitation_strat != "WW" and elicitation_strat != "ALL"
                and elicitation_strat != "BB" and elicitation_strat != "BW"):
            elicitation_strat = "ALL"
            budget = float('inf')



    runs = 10
    for i in range(0,runs):

        start = time.time()
        LSP = LocalSearch_IWCSP(name = '1', file_path = filepath, tabu_list_maxsize = 1000, elicitation_strat = elicitation_strat, budget = budget)
        LSP.solve(iterations = iterations, p = 0.20)
        end = time.time()
        runtime = end - start
        preferences.append(LSP.compute_preference(LSP.current_assign)[0])
        runtimes.append(runtime)
        elicitation_cost.append(LSP.elicitation_cost)
        elicitation_numbers.append(LSP.elicitation_number)



    print ('number of runs: ' + str(runs))
    print ('Elicitation Strategy: ' + elicitation_strat)
    print ('preference: ' + str((sum(preferences)/ len(preferences))))
    print ('runtime: ' + str((sum(runtimes)/ len(runtimes))))
    print ('elicitation_cost: ' + str((sum(elicitation_cost)/ len(elicitation_cost))))
    print ('number of elicitations: ' + str((sum(elicitation_numbers)/ len(elicitation_numbers))))
    print ('final assignment: ' + str(LSP.current_assign))


if __name__ == "__main__":
    main()
