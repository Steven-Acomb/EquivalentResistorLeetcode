# Equivalent Resistance

## Background

When designing circuits, we often need to choose components based on parameter values such as resistance/capacitance for resistors/capacitors. In many cases however, there don't exist any physical components with the exact, theoretically ideal parameter values we calculate for our designs. In these circumstances, electrical engineers typically solve the problem by taking advantage of the fact that many components such as resistors and capacitors can be connected in configurations which result in them behaving together as if they were a single component with a different parameter value.

For example, two resistors with resistances Ra and Rb can be arranged in series to behave like a single resistor with equivalent resistance `Req = Ra + Rb`, or in parallel to behave like a single resistor with equivalent resistance `Req = 1 / ((1/Ra) + (1/Rb))`. Capacitors work the same way, except the equations are swapped, with the aforementioned parallel relationship resulting from the capacitors physically connected in series and vice-versa.

Although manufacturers produce components like resistors and capacitors with many different values for their respective parameters, such diversity is expensive. As a result, the industry has settled on a few sets of standard parameter values which have been chosen because they allow engineers to construct a broad range of equivalent components from a small pool of parameter values actually embodied in real, physical ones. This works well in practice, largely thanks to the nature of the equations governing equivalent resistance and capacitance, since you can in theory produce an equivalent component with a parameter value of any rational number, even if you only have a bunch of base components with a single parameter value, so long as that value is rational and you can produce your equivalent with sufficiently many of them. You can even produce equivalent components with irrational equivalent parameter values, so long as the set of base parameter values you're working from contains a value of any rational number times that irrational number. (On this note, one thing I personally think you should consider if you want to give this a shot is that relative to their inputs, one function is monotonically increasing and the other decreasing.)

In practice of course, engineers have to balance many tradeoffs in their designs, and reproducing an exact equivalent component with some theoretically derived ideal value for your application using an unlimited quantity of base components is generally less cost-effective than producing a close approximate using fewer, so we often simply do that instead. This, however, introduces the additional wrinkle of choosing which approximate is best for the application, and how many base components is it worth using to produce the desired equivalent. That's a much larger issue than it may sound, as the set of possible equivalents which can be produced from a given number of components with parameter values chosen from a given set has a size with a factorial relationship to the number of available base values and the maximum number of actual base components with them we allow for use in producing our equivalent. Knowing how much closer using an additional base component would make the approximation's equivalent value to the theoretical ideal is very important for making a good design decision, yet it turns out that this is quite time-consuming to calculate.

In the past, I have attempted to automate doing this with a script which calculates the set of possible equivalents and selects the best by brute force with some minor optimizations, however as you may guess this approach is unacceptably inefficient for many scenarios. Another issue I ran into is that it's not enough to calculate the possible values for the equivalent component, you also have to be able to tell the user how to construct it from the base components.

## Problem

Given an array of double `baseResistances` representing available base resistance values, an integer `maxResistors` representing the maximum number of components you're allowed to use to produce an equivalent resistor, and a double `resistance` representing a theoretical ideal resistance, return a string which encodes in **"Serializable Configuration Format"** (SCF) a **"configuration"** of base resistors that combine to behave as an equivalent resistor that is an **"optimal approximation"**.

An equivalent resistor is an **"optimal approximation"** if it satisfies both of the following conditions for the given set of base values and maximum component count:
1. The difference between the equivalent's resistance and the ideal is the minimum value possible for any equivalent resistor satisfying the constraints.
2. The equivalent resistor is produced using the minimum number of base resistors possible out of any configuration producing that equivalent resistance value.

### Definitions

A **"configuration"** is a particular collection of components with specific parameter values and specific arrangement, thus resulting in the whole system behaving as a single equivalent instance of that type of component with some equivalent parameter value equal to the result of composing the functions according to the arrangement of the base components.

**"Serializable Configuration Format"** (SCF) is a format for representing configurations of components as strings. SCF strings consist of a set of nested parentheses, each representing an equivalent parameter value, as well as the symbol and inputs of the mathematical function which produces it, if applicable. These inputs are each their own set of nested parentheses, as they themselves represent parameter values encoded in SCF. An SCF string consisting solely of an integer between a single set of parentheses represents a base component, particularly an instance of a base component with the parameter value at the corresponding index of the array of base components (e.g. `baseResistances`). Otherwise, the interior of an SCF string consists of two inputs separated by either `//` or `+`, representing the resistor parallel and series configurations respectively.

**SCF Example:** Given `baseResistances = [1, 1.5, 2.7, 4.3, 4.7]`, the SCF string `((0)//(4))+((3)//(2))` represents an equivalent resistance of about 2.48313, constructed by placing an equivalent resistance of about 0.824561 in series with an equivalent resistance of about 1.658571, where the 0.824561 is constructed by placing a base resistor of 1 ohm in parallel with a base resistor of 4.7 ohms, and the 1.658571 is constructed by placing a base resistor of 4.3 ohms in parallel with a base resistor of 2.7 ohms.

## Examples

### Example 1

```
Input:  baseResistances = [1, 5, 10], idealResistance = 3.01, maxResistors = 3
Output: Either "((0)+(0))+(0)" or "(0)+((0)+(0))" will be accepted.
```

**Explanation:** It is valid to use multiple base resistors of the same value. You are not limited in how many values you use out of those available for your base resistors, nor are you limited in how many base resistors you use of any given value so long as the total number of base resistors you use is at most `maxResistors`. As such, `(1)` is not an optimal approximation, since there exists a valid configuration of at most 3 base resistors which produces an equivalent resistance (3) which is closer to 3.01 ohms than the 5 ohm equivalent that `(1)` represents.

### Example 2

```
Input:  baseResistances = [10, 20], idealResistance = pi * 10, maxResistors = 5
Output: "((1)+((1)//((1)+((0)//(1)))))" or any synonymous SCF string will be accepted.
```

**Explanation:** This SCF string represents a configuration of base resistors with equivalent resistance around 31.42857, the closest to pi\*10 of any possible configuration of at most 5 resistors whose values can each be either 10 or 20 ohms. Note: the test harness directly computes the equivalent resistance represented by your output string, so SCF strings representing analogous configurations all work if they produce the same equivalent resistance and number of components.

### Example 3

```
Input:  baseResistances = [1, 8], idealResistance = 2.1, maxResistors = 4
Output: "(0)+(0)"
```

**Explanation:** Although you can use up to 4 resistors to produce an equivalent, the closest value possible is still 2, which only requires two resistors (1 ohm in series with 1 ohm). While `((1)//(1))//((1)//(1))` still produces a 2 ohm equivalent resistance, this configuration does not meet condition #2 for qualifying as an optimal approximation.

## Constraints

- For this example, your solution needn't be extensible to components besides resistors.
- Your solution may be within +/- 0.0001% of the expected value to account for floating point arithmetic.
- You can reliably assume that neither array sizes nor output string lengths will exceed language-specific limits.
- Your code must be efficient enough (at a minimum!) to pass the included tests with the default heap size.

## Clarification

As a mental image for pure software people, picture standing in front of a cabinet with one drawer for each entry in the `baseResistances` array. Each drawer contains an infinite number of resistors, each resistor having the same resistance as all the others in its drawer, corresponding to that entry. (e.g. `[1, 5, 10]` being a cabinet with 3 drawers, the 1st containing a bunch of 1 ohm resistors, the 2nd having a bunch of 5 ohm resistors, and the 3rd having a bunch of 10 ohm resistors.)

You are tasked with taking resistors from the cabinet (from any combination of the drawers) and sticking them in a breadboard such that the equivalent resistance between two of the terminals is as close to the ideal as you can, given the restrictions that you take at most `maxResistors`, and only have access to the kinds of resistors which that cabinet has drawers for.

A "base" resistor is the real, physical object you can take from one of the drawers of the cabinet, while an "equivalent resistor" would be the little circuit you make out of them on the breadboard. Since that little circuit electrically behaves as if it were just another kind of resistor with a different resistance value, including the fact that you can make even more elaborate equivalent resistors with them, you can create a wide variety of values by connecting a bunch of them in different ways. The restriction in this problem is therefore on how many of those physical "base" resistors you use, not how many types of resistors, and not how many resistance values you use or generate intermediately.

## Available Utilities

Each language provides a utility library (`resistor_utils` in Python, `ResistorUtils` in Java) with helper functions you can use in your solution. These are already imported in the solution stub.

### `series(a, b)` / `series(double a, double b)`

Computes the equivalent resistance of two resistors in series.

Returns `a + b`.

```
series(1.0, 2.0)  →  3.0
series(10.0, 20.0)  →  30.0
```

### `parallel(a, b)` / `parallel(double a, double b)`

Computes the equivalent resistance of two resistors in parallel.

Returns `1 / (1/a + 1/b)`.

```
parallel(3.0, 6.0)  →  2.0
parallel(10.0, 10.0)  →  5.0
```

### `base_scf(index)` / `baseScf(int index)`

Returns the SCF string for a single base resistor at the given index in `baseResistances`.

```
base_scf(0)  →  "0"
base_scf(3)  →  "3"
```

### `combine_scf(left, right, op)` / `combineScf(String left, String right, String op)`

Combines two SCF strings with a series (`"+"`) or parallel (`"//"`) operator. Wraps each operand in parentheses.

```
combine_scf("0", "1", "+")    →  "(0)+(1)"
combine_scf("0", "1", "//")   →  "(0)//(1)"
combine_scf("(0)+(1)", "2", "//")  →  "((0)+(1))//(2)"
```

### `evaluate_config(scf, base_resistances)` / `evaluateConfig(String scf, double[] baseResistances)`

Parses an SCF string and computes the equivalent resistance it represents, given an array of base resistance values. This is the same function the test harness uses to verify your answer.

```
evaluate_config("0", [1, 2])          →  1.0
evaluate_config("(0)+(1)", [1, 2])    →  3.0
evaluate_config("(0)//(1)", [3, 6])   →  2.0
```

## Hint

Relative to their inputs, one combination function is monotonically increasing and the other is monotonically decreasing.
