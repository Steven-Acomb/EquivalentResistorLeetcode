package com.stephenacomb;

import java.util.function.BiFunction;

// Imports for Naive Brute-Force Implementation
import java.util.ArrayList;

public class ResistorApproximator {
	
	private double[] baseResistances;
	
	public ResistorApproximator(double[] baseResistances) {
		this.baseResistances = baseResistances;
	}
	
	public String approximateBruteForceNaive(double resistance, int maxResistors){
		// Create recipies for base resistances
		ArrayList<String> baseRecipies = new ArrayList<String>();
		for(int k=0; k<baseResistances.length; k++){
			String baseRecipie = "("+String.valueOf(k)+")";
			baseRecipies.add(baseRecipie);
		}

		// Create cookbook and add base recipies as the recipies for values using just 1 resistor
		ArrayList<ArrayList<String>> cookbook = new ArrayList<ArrayList<String>>();
		cookbook.add(baseRecipies);

		// Create recipies for all values using n resistors & add them to cookbook
		// For all recipies of previous tier, add series and parallel recipies for base resistances
		// for all tiers...
		for(int n=1; n<maxResistors; n++){
			ArrayList<String> tierRecipies = new ArrayList<String>();
			// for all recipies in previous tier...
			for(int i=0; i<cookbook.get(n-1).size(); i++){
				String recipie = cookbook.get(n-1).get(i);
				// for all base resistors...
				for(int j=0; j<baseResistances.length; j++){
					// add additional series recipie
					String tierSeriesRecipie = "("+recipie+"+("+String.valueOf(j)+"))";
					tierRecipies.add(tierSeriesRecipie);
					// add additional parallel recipie
					String tierParallelRecipie = "("+recipie+"//("+String.valueOf(j)+"))";
					tierRecipies.add(tierParallelRecipie);
				}
			}
			cookbook.add(tierRecipies);
		}

		// print cookbook for debugging
		System.out.println("Cookbook for target = " + String.valueOf(resistance) + ", maxResistors = " + String.valueOf(maxResistors));
		System.out.println("cookbook.size() = " + String.valueOf(cookbook.size()));
		for(int k = 0; k<cookbook.size();k++){
			System.out.println("Tier " + String.valueOf(k) + " has " + String.valueOf(cookbook.get(k).size()) + " values.");
		}

		// iterate through all possibilities to find closest value
		double minimumError = Math.abs(Double.MAX_VALUE);
		double error; // minimumError = Math.abs();
		ArrayList<String> tier;
		String bestRecipie = "(0)";
		String recipie;
		// iterate through all tiers
		for(int k = 0; k<cookbook.size();k++){
			// iterate through all recipies
			tier = cookbook.get(k);
			for(int l = 0; l<tier.size();l++){
				recipie = tier.get(l);
				error = Math.abs(evaluateResistorConfiguration(recipie)-resistance);
				System.out.println("recipie = " + recipie);
				System.out.println("error = " + String.valueOf(error) + ", minimumError = " + String.valueOf(minimumError));
				if(error < minimumError){
					minimumError = error;
					bestRecipie = recipie;
				}
			}
		}
		System.out.println("bestRecipie = " + bestRecipie);
		return bestRecipie;
	}

	public String approximate(double resistance, int maxResistors){
		//TODO: Write this method
		return approximateBruteForceNaive(resistance, maxResistors);
		// return "(0)";
		// String recipe = "(((0)+(0))+(((0)+(0))//(((0)+(0))+((0)//((0)+(0))))))";
		// System.out.println(String.valueOf(evaluateResistorConfiguration(recipe)));
		// return recipe;
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
