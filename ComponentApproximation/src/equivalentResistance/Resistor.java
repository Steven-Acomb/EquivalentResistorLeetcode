package equivalentResistance;

import java.util.function.BiFunction;
import java.util.Map;

public class Resistor {	
	public static Map<String,BiFunction<Double,Double,Double>> functions(){
		class ResistorSeriesFunction implements BiFunction<Double,Double,Double>{
			public ResistorSeriesFunction() {}
			@Override
			public Double apply(Double t, Double u) {return t+u;}
		}
		
		class ResistorParallelFunction implements BiFunction<Double,Double,Double>{
			public ResistorParallelFunction() {}
			@Override
			public Double apply(Double t, Double u) {return 1/((1/t)+(1/u));}
		}
		
		return Map.of("+",new ResistorSeriesFunction(), 
				"//", new ResistorParallelFunction());
	}
}
