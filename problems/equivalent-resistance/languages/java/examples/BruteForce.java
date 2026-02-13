package com.stephenacomb;

import static com.stephenacomb.ResistorUtils.*;
import java.util.*;

public class Solution implements Solver {

	/**
	 * Brute-force DP approach:
	 * dp[n] = all distinct (equivalentResistance -> config) pairs achievable with exactly n resistors.
	 * For each component count, combine dp[i] x dp[n-i] via series and parallel.
	 * Track the overall best across all component counts.
	 */
	public String approximate(double[] baseResistances, double resistance, int maxResistors) {
		boolean targetMax = (resistance == Double.MAX_VALUE);

		// dp[n] maps equivalent resistance value -> Config node
		@SuppressWarnings("unchecked")
		Map<Double, Config>[] dp = new HashMap[maxResistors + 1];

		// Base case: single resistors
		dp[1] = new HashMap<>();
		for (int i = 0; i < baseResistances.length; i++) {
			dp[1].putIfAbsent(baseResistances[i], new Config(i));
		}

		// Track overall best
		Config bestConfig = null;
		double bestDiff = Double.MAX_VALUE;
		int bestCount = Integer.MAX_VALUE;

		// Check single resistors
		for (Map.Entry<Double, Config> e : dp[1].entrySet()) {
			double diff = computeDiff(e.getKey(), resistance, targetMax);
			if (isBetter(diff, 1, bestDiff, bestCount)) {
				bestDiff = diff;
				bestCount = 1;
				bestConfig = e.getValue();
			}
		}

		// Build dp[2..maxResistors]
		for (int n = 2; n <= maxResistors; n++) {
			dp[n] = new HashMap<>();

			for (int i = 1; i <= n / 2; i++) {
				int j = n - i;
				if (dp[i] == null || dp[j] == null) continue;

				for (Map.Entry<Double, Config> le : dp[i].entrySet()) {
					double lVal = le.getKey();
					Config lCfg = le.getValue();

					for (Map.Entry<Double, Config> re : dp[j].entrySet()) {
						double rVal = re.getKey();
						Config rCfg = re.getValue();

						// Series combination
						double sVal = series(lVal, rVal);
						if (!dp[n].containsKey(sVal)) {
							dp[n].put(sVal, new Config(lCfg, rCfg, true));
						}

						// Parallel combination
						double pVal = parallel(lVal, rVal);
						if (!dp[n].containsKey(pVal)) {
							dp[n].put(pVal, new Config(lCfg, rCfg, false));
						}
					}
				}
			}

			// Check this component count for improvements
			for (Map.Entry<Double, Config> e : dp[n].entrySet()) {
				double diff = computeDiff(e.getKey(), resistance, targetMax);
				if (isBetter(diff, n, bestDiff, bestCount)) {
					bestDiff = diff;
					bestCount = n;
					bestConfig = e.getValue();
				}
			}

			// If dp[n] is empty (shouldn't happen but safety), skip
			if (dp[n].isEmpty()) dp[n] = null;
		}

		return bestConfig.toScf();
	}

	private double computeDiff(double val, double target, boolean targetMax) {
		if (targetMax) return -val; // maximize: smaller (more negative) is better
		return Math.abs(val - target);
	}

	private boolean isBetter(double diff, int count, double bestDiff, int bestCount) {
		if (diff < bestDiff) return true;
		if (diff == bestDiff && count < bestCount) return true;
		return false;
	}

	/** Lightweight tree node representing a resistor configuration. */
	private static class Config {
		final int baseIndex;      // >= 0 for leaf, -1 for internal node
		final Config left, right;
		final boolean isSeries;   // true = "+", false = "//"

		/** Leaf: a single base resistor. */
		Config(int baseIndex) {
			this.baseIndex = baseIndex;
			this.left = this.right = null;
			this.isSeries = false;
		}

		/** Internal: combination of two sub-configurations. */
		Config(Config left, Config right, boolean isSeries) {
			this.baseIndex = -1;
			this.left = left;
			this.right = right;
			this.isSeries = isSeries;
		}

		/** Convert this tree to an SCF string. */
		String toScf() {
			if (baseIndex >= 0) return baseScf(baseIndex);
			return combineScf(left.toScf(), right.toScf(), isSeries ? "+" : "//");
		}
	}
}
