package com.stephenacomb;

import java.util.Map;
import java.util.function.BiFunction;

public class ResistorUtils {

	public static double series(double a, double b) {
		return a + b;
	}

	public static double parallel(double a, double b) {
		return 1 / ((1 / a) + (1 / b));
	}

	public static String baseScf(int index) {
		return String.valueOf(index);
	}

	public static String combineScf(String left, String right, String op) {
		return "(" + left + ")" + op + "(" + right + ")";
	}

	public static double evaluateConfig(String configuration, double[] baseResistances) {
		int len = configuration.length();
		if (configuration.charAt(0) != '(')
			return baseResistances[Integer.parseInt(configuration)];
		else {
			int parentheses = 1;
			for (int i = 1; i < len; i++) {
				if (configuration.charAt(i) == '(')
					parentheses++;
				else if (configuration.charAt(i) == ')')
					parentheses--;
				if (parentheses == 0) {
					int[] splits = getSplits(configuration.substring(i));
					if (splits[0] == -1)
						return evaluateConfig(configuration.substring(1, i), baseResistances);
					BiFunction<Double, Double, Double> operation = functions().get(
							configuration.substring(i + splits[0], i + splits[1]));
					return operation.apply(
							Double.valueOf(
									evaluateConfig(
											configuration.substring(1, i), baseResistances)),
							Double.valueOf(
									evaluateConfig(
											configuration.substring(i + splits[1] + 1, len - 1), baseResistances)));
				}
			}
		}
		return -1;
	}

	private static int[] getSplits(String config) {
		int[] splits = new int[2];
		int firstOpChar = -1;
		int lastOpCharPP = -1;
		String[] opSymbols = new String[] { "+", "//" };
		for (int i = 0; i < config.length(); i++) {
			for (String opStr : opSymbols) {
				if (config.charAt(i) == opStr.charAt(0)) {
					firstOpChar = i;
					lastOpCharPP = i + opStr.length();
					splits[0] = firstOpChar;
					splits[1] = lastOpCharPP;
					return splits;
				}
			}
		}
		splits[0] = firstOpChar;
		splits[1] = lastOpCharPP;
		return splits;
	}

	private static Map<String, BiFunction<Double, Double, Double>> functions() {
		return Map.of(
				"+", (a, b) -> a + b,
				"//", (a, b) -> 1 / ((1 / a) + (1 / b)));
	}
}
