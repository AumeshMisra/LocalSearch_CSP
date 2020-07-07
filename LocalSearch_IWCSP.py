import random

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
        self.starting_assign = self.get_starting_assign()

    #choose random starting assignment
    def get_starting_assign(self):
        starting_dict = {key: random.randint(1, self.domainrange) for key in self.varList}
        return starting_dict


    #chooses variable that should be updated in local search
    def choose_variable(self):
        pass

    #chooses value for variable that should be updated in local search
    def choose_value_for_variable(self, variable):
        pass


LSP = LocalSearch_IWCSP('1')
print (LSP.input, LSP.varList, LSP.domainrange, LSP.incompTable, LSP.starting_assign)
