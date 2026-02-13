package com.stephenacomb;

import static com.stephenacomb.ResistorUtils.*;

public class Solution implements Solver {

	public String approximate(double[] baseResistances, double resistance, int maxResistors) {
		// TODO: Implement your solution here.
		//
		// Available utilities (from ResistorUtils):
		//   series(a, b)                          — returns a + b
		//   parallel(a, b)                        — returns 1/((1/a)+(1/b))
		//   evaluateConfig(scf, baseResistances)  — evaluates an SCF string to a resistance value
		//   baseScf(index)                        — returns the SCF string for a base resistor
		//   combineScf(left, right, op)           — combines two SCF strings with "+" or "//"
		return baseScf(0);
	}
}
