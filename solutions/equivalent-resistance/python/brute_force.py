import math
from solver import Solver
from resistor_utils import series, parallel, evaluate_config, base_scf, combine_scf


class Solution(Solver):

    def approximate(self, base_resistances, resistance, max_resistors):
        target = resistance

        # configs[n] maps resistance_value -> scf_string for exactly n resistors
        configs = {}

        # Level 1: single base resistors
        configs[1] = {}
        for i, r in enumerate(base_resistances):
            if r not in configs[1]:
                configs[1][r] = base_scf(i)

        # Build levels 2..max_resistors
        for n in range(2, max_resistors + 1):
            configs[n] = {}
            for i in range(1, n // 2 + 1):
                j = n - i
                if i not in configs or j not in configs:
                    continue
                for val_a, scf_a in list(configs[i].items()):
                    for val_b, scf_b in list(configs[j].items()):
                        # Series
                        s = val_a + val_b
                        if s not in configs[n]:
                            configs[n][s] = combine_scf(scf_a, scf_b, "+")

                        # Parallel
                        if val_a > 0 and val_b > 0:
                            p = 1.0 / (1.0 / val_a + 1.0 / val_b)
                            if p not in configs[n]:
                                configs[n][p] = combine_scf(scf_a, scf_b, "//")

        # Find best across all levels: closest to target, then fewest resistors
        best_scf = base_scf(0)
        best_diff = self._diff(base_resistances[0], target)
        best_count = 1

        for n in range(1, max_resistors + 1):
            if n not in configs:
                continue
            for val, scf in configs[n].items():
                d = self._diff(val, target)
                if d < best_diff or (d == best_diff and n < best_count):
                    best_diff = d
                    best_count = n
                    best_scf = scf

        return best_scf

    def _diff(self, val, target):
        if target == float("inf"):
            return -val  # maximize: more negative = better
        elif target == 0:
            return val  # minimize: lower = better
        else:
            return abs(val - target)
