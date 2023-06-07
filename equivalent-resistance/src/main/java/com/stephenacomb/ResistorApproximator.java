package com.stephenacomb;

import java.util.function.BiFunction;

public class ResistorApproximator {
	
	private double[] baseResistances;
	
	public ResistorApproximator(double[] baseResistances) {
		this.baseResistances = baseResistances;
	}
	
	public String approximate(double resistance, int maxResistors){
		//TODO: Write this method
		return "(0)";
	}
	
	private int[] getSplits(String config) {
		int[] splits = new int[2];
		int firstOpChar = -1;
		int lastOpCharPP = -1;
		String[] opSymbols = new String[] {"+","//"};
		for(int i = 0; i < config.length(); i++) {
			for(String opStr : opSymbols) {
				if(config.charAt(i) == opStr.charAt(0)) {
					firstOpChar = i;
					lastOpCharPP = i+opStr.length();
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
	
	public double evaluateResistorConfiguration(String configuration) {
		int len = configuration.length();
		if(configuration.charAt(0) != '(')
			return baseResistances[Integer.parseInt(configuration)];
		else {
			int parentheses = 1;			
			for(int i = 1; i<len; i++) {
				if(configuration.charAt(i) == '(')
					parentheses++;
				else if(configuration.charAt(i) == ')')
					parentheses--;
				if(parentheses == 0) {
					int[] splits = getSplits(configuration.substring(i));
					if(splits[0] == -1) 
						return evaluateResistorConfiguration(configuration.substring(1,i));
					BiFunction<Double,Double,Double> operation = Resistor.functions().get(
							configuration.substring(i+splits[0],i+splits[1]));
					return operation.apply(
							Double.valueOf(
									evaluateResistorConfiguration(
											configuration.substring(1,i))), 
							Double.valueOf(
									evaluateResistorConfiguration(
											configuration.substring(i+splits[1]+1,len-1))));
				}
			}
		}
		return -1;
	}
	
}
