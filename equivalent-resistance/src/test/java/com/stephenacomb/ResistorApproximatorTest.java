package com.stephenacomb;

import static org.junit.Assert.assertEquals;

import org.junit.AfterClass;
import org.junit.Test;

public class ResistorApproximatorTest {
	
	private static float points = 0;
	private static final double DELTA = 1e6;

	private ResistorApproximator exampleApproximator() {
		double[] baseResistances = new double[] {
				1, 1.5, 2.7, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 
				8.2, 9.1, 10, 11, 12, 13, 15, 16, 18, 20, 
				22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 
				56, 62, 68, 75, 82, 91, 100, 110, 120, 130, 
				150, 160, 180, 200, 220, 240, 270, 300, 330, 360, 
				390, 430, 470, 510, 560, 620, 680, 750, 820, 910, 
				1000, 1100, 1200, 1300, 1500, 1600, 1800, 2000, 2200, 2400, 
				2700, 3000, 3300, 3600, 3900, 4500, 4700, 5100, 5600, 6200, 
				7500, 8200, 9100, 10000, 11000, 12000, 13000, 15000, 16000, 18000, 
				20000, 22000, 24000, 27000, 30000, 33000, 36000, 39000, 43000, 47000, 
				51000, 56000, 62000, 68000, 75000, 82000, 91000, 100000, 110000, 120000, 
				130000, 150000, 160000, 180000, 200000, 220000, 240000, 270000, 300000, 330000, 
				360000, 390000, 430000, 470000, 510000, 560000, 620000, 680000, 750000, 820000, 910000, 
				1000000, 1100000, 1200000, 1300000, 1500000, 1600000, 1800000, 2000000, 2100000, 2200000, 
				2400000, 2700000, 3000000, 3300000, 3600000, 3900000, 4700000, 5600000, 6800000, 8200000, 
				10000000
				};
		return new ResistorApproximator(baseResistances);
	}
	
	@Test
	public void test1() {
		ResistorApproximator apx = exampleApproximator();
		String config = "((0)//(4))+((3)//(2))"; // ~= 2.48313
		int maxResistors = 4;
		double expected = apx.evaluateResistorConfiguration(config);
		double actual = apx.evaluateResistorConfiguration(apx.approximate(expected, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}
	
	@Test
	public void test2() {
		double[] baseResistances = new double[] {1,2};
		ResistorApproximator apx = new ResistorApproximator(baseResistances);
		String config = "((1)+((1)//((1)+((0)//(1)))))"; // ~= 3.142857142857143
		int maxResistors = 5;
		double expected = apx.evaluateResistorConfiguration(config);
		double actual = apx.evaluateResistorConfiguration(apx.approximate(expected, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}
	
	@Test
	public void test3() {
		double[] baseResistances = new double[] {1,1000};
		ResistorApproximator apx = new ResistorApproximator(baseResistances);
		String config = "(0)//((0)//((0)//((0)//((0)//((0)//((0)//(0)))))))"; // ~= 0.125
		int maxResistors = 8;
		double expected = apx.evaluateResistorConfiguration(config);
		double actual = apx.evaluateResistorConfiguration(apx.approximate(0, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}
	
	@Test
	public void test4() {
		double[] baseResistances = new double[] {0.1,1};
		ResistorApproximator apx = new ResistorApproximator(baseResistances);
		String config = "(1)+((1)+((1)+((1)+((1)+((1)+((1)+(1)))))))"; // ~= 8
		int maxResistors = 8;
		double expected = apx.evaluateResistorConfiguration(config);
		double actual = apx.evaluateResistorConfiguration(
				apx.approximate(Double.MAX_VALUE, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}
	
	@Test
	public void test5() {
		double[] baseResistances = new double[] {
				336, 420, 480, 560, 630, 672, 
				720, 840, 960, 1008, 1050, 1120, 
				1200, 1260, 1344, 1400, 1440, 1680, 
				1960, 2016, 2100, 2240, 2352, 2520, 
				2688, 2800, 2940, 3360, 3920, 4200, 
				4480, 5040, 5880, 6720, 8400
				};
		ResistorApproximator apx = new ResistorApproximator(baseResistances);
		int maxResistors = 3;
		double expected = 11200.0/3;
		double actual = apx.evaluateResistorConfiguration(
				apx.approximate(Double.MAX_VALUE, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}
	
	@Test
	public void test6() {
		double[] baseResistances = new double[] {1680};
		ResistorApproximator apx = new ResistorApproximator(baseResistances);
		int maxResistors = 8;
		double expected = 11200.0/3;
		double actual = apx.evaluateResistorConfiguration(apx.approximate(expected, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}
	
	@Test
	public void test7() {
		double[] baseResistances = new double[] {13};
		ResistorApproximator apx = new ResistorApproximator(baseResistances);
		int maxResistors = 13;
		double expected = 1;
		double actual = apx.evaluateResistorConfiguration(apx.approximate(expected, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}
	
	@Test
	public void test8() {
		double[] baseResistances = new double[] {17};
		ResistorApproximator apx = new ResistorApproximator(baseResistances);
		int maxResistors = 11;
		double expected = 19;
		double actual = apx.evaluateResistorConfiguration(apx.approximate(expected, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}

	// Specific tests for simpler case where you only have one base resistance to build your equivalent from: 
	@Test
	public void test9() {
		double[] baseResistances = new double[] {1};
		ResistorApproximator apx = new ResistorApproximator(baseResistances);
		int maxResistors = 9;
		String config = "(((0)+(0))+(((0)+(0))//(((0)+(0))+((0)//((0)+(0))))))"; // = 22/7 ~= 3.142857142857143
		double expected = apx.evaluateResistorConfiguration(config);
		double actual = apx.evaluateResistorConfiguration(apx.approximate(expected, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}

	@Test
	public void test10() {
		double[] baseResistances = new double[] {1};
		ResistorApproximator apx = new ResistorApproximator(baseResistances);
		int maxResistors = 4;
		String config = "((0)+((0)//((0)//(0))))"; // = 4/3 ~= 1.3333333333333333
		double expected = apx.evaluateResistorConfiguration(config);
		double actual = apx.evaluateResistorConfiguration(apx.approximate(expected, maxResistors));
		assertEquals(expected, actual, (expected/DELTA));
		points += 1.0;
	}
	
	@AfterClass
	public static void showPoints() {
		System.out.printf("RESISTOR_APPROXIMATOR POINTS = %.1f of 10.0\n", points);
	}

}
