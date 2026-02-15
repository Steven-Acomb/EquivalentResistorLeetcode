from resistor_utils import base_scf, combine_scf, evaluate_config, parallel, series
from solver import Solver


class Solution(Solver):

    def stern_brocot_nearest(self, stern_brocot_target, max_steps):
        """
        Binary search the Stern-Brocot tree to find the nearest fraction to
        stern_brocot_target within max_steps steps (i.e. depth max_steps + 1).

        Returns the L/R path as a list, e.g. ['R', 'L', 'L'].
        The path for the root (1/1) is [].
        """
        target = stern_brocot_target

        # Stern-Brocot bounds: mediants are computed from these
        l_num, l_den = 0, 1  # left bound  = 0/1
        r_num, r_den = 1, 0  # right bound = 1/0 (infinity)

        # Root mediant = 1/1
        m_num, m_den = 1, 1

        path = []
        best_path = []
        best_val = m_num / m_den

        for _ in range(max_steps):
            m_val = m_num / m_den
            if m_val == target:
                break

            if target > m_val:
                path.append("R")
                l_num, l_den = m_num, m_den
            else:
                path.append("L")
                r_num, r_den = m_num, m_den

            m_num = l_num + r_num
            m_den = l_den + r_den

            new_val = m_num / m_den
            if self._closer(new_val, best_val, target):
                best_path = path[:]
                best_val = new_val

        return best_path

    def _closer(self, a, b, target):
        """Return True if a is strictly closer to target than b."""
        if target == float("inf"):
            return a > b
        if target == 0:
            return a < b
        return abs(a - target) < abs(b - target)

    def cw_path_to_scf(self, cw_path, index):
        """
        Convert a Calkin-Wilf tree path to an SCF string.

        In the Calkin-Wilf tree, the root represents a single base resistor.
        Each step adds one more base resistor:
          - L (left child)  = put current equivalent in parallel with a base resistor
          - R (right child) = put current equivalent in series with a base resistor

        This directly builds the resistor configuration string.
        """
        scf = base_scf(index)
        for step in cw_path:
            if step == "R":
                scf = combine_scf(scf, base_scf(index), "+")
            else:
                scf = combine_scf(scf, base_scf(index), "//")
        return scf

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
        if len(base_resistances) != 1:
            raise
        if max_resistors < 2:
            return base_scf(0)
        # Broad Steps:
        # 1. Divide target resistance by sole base resistance
        stern_brocot_target = resistance / base_resistances[0]
        # 2. The Stern–Brocot tree is a binary search tree. Do binary search down to nth level where n = max_resistors (or stop short) to find the nearest possible value
        best_path = self.stern_brocot_nearest(stern_brocot_target=stern_brocot_target, max_steps=max_resistors - 1)
        print("best_path = ", best_path)
        # 3. The Calkin–Wilf tree has the same numbers each layer as the Stern–Brocot tree but the way it's structured actually corresponds to the values produced by
        #       single-resistance series/parallel connections. There's a correspondance that we should be able to do which takes the position of a node in the
        #       Stern–Brocot tree and finds the corresponding position in the Calkin–Wilf tree in minimal time. Do so for our nearest value from step 2.
        best_path_cw = best_path[::-1]
        print("best_path_cw = ", best_path_cw)
        # 4. Since the series/parallel combinations for our one resistor type are encoded in the Calkin–Wilf tree, we should be able to use our position to find the
        #       SCF string for our nearest value. Do so and return that SCF string.
        best_scf = self.cw_path_to_scf(cw_path=best_path_cw, index=0)
        print("best_scf = ", best_scf)

        return best_scf


# python3 -m engine run -p equivalent-resistance -l python -s solutions/equivalent-resistance/python/stephen_tree_solution.py
# conda activate equivresistor
# python3 -m server
# PYTHONPATH=problems/equivalent-resistance/languages/python python solutions/equivalent-resistance/python/stephen_tree_solution.py

# solution = Solution()
# base_resistances = [2]
# resistance = (2 / 3 - 0.01) * 2
# max_resistors = 4
# solution.approximate(base_resistances, resistance, max_resistors)
# print("done")
