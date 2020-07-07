from abc import ABC, abstractmethod

class LocalSearchProblem(ABC):

    @abstractmethod
    def get_starting_assign(self):
        pass

    #chooses variable that should be updated in local search
    @abstractmethod
    def choose_variable(self):
        pass

    #chooses value for variable that should be updated in local search
    @abstractmethod
    def choose_value_for_variable(self, variable):
        pass
