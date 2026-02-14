from solver import Solver
from resistor_utils import series, parallel, evaluate_config, base_scf, combine_scf


class Solution(Solver):

    def approximate(self, base_resistances, resistance, max_resistors):
        # TODO: Implement your solution here.
        #
        # Available utilities (from resistor_utils):
        #   series(a, b)                            — returns a + b
        #   parallel(a, b)                          — returns 1 / (1/a + 1/b)
        #   evaluate_config(scf, base_resistances)  — evaluates an SCF string to a resistance value
        #   base_scf(index)                         — returns the SCF string for a base resistor
        #   combine_scf(left, right, op)            — combines two SCF strings with "+" or "//"
        return base_scf(0)
