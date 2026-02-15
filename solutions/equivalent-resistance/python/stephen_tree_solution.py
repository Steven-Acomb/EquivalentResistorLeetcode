from resistor_utils import base_scf, combine_scf, evaluate_config, parallel, series
from solver import Solver


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

        # Current version of algorithm only works for the len(base_resistances) == 1 case.
        # Broad Steps:
        # 1. Divide target resistance by sole base resistance
        # 2. The Stern–Brocot tree is a binary search tree. Do binary search down to nth level where n = max_resistors (or stop short) to find the nearest possible value
        # 3. The Calkin–Wilf tree has the same numbers each layer as the Stern–Brocot tree but the way it's structured actually corresponds to the values produced by
        #       single-resistance series/parallel connections. There's a correspondance that we should be able to do which takes the position of a node in the
        #       Stern–Brocot tree and finds the corresponding position in the Calkin–Wilf tree in minimal time. Do so for our nearest value from step 2.
        # 4. Since the series/parallel combinations for our one resistor type are encoded in the Calkin–Wilf tree, we should be able to use our position to find the
        #       SCF string for our nearest value. Do so and return that SCF string.

        return base_scf(0)


# python3 -m engine run -p equivalent-resistance -l python -s solutions/equivalent-resistance/python/stephen_tree_solution.py
# conda activate equivresistor
# python3 -m server
