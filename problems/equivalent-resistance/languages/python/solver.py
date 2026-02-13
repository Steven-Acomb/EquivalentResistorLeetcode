from abc import ABC, abstractmethod


class Solver(ABC):
    @abstractmethod
    def approximate(self, base_resistances, resistance, max_resistors):
        pass
