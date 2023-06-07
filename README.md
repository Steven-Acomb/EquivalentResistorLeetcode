# EquivalentResistorLeetcode
Test package for my custom Leetcode problem. Please give it a try! 

I'd love to see what you come up with.

**Background:**

When designing circuits, we often need to choose components based on parameter values such as resistance/capacitance for resistors/capacitors.
In many cases however, there don't exist any physical components with the exact, theoretically ideal parameter values we calculate for our designs.
In therse circumstances, electrical engineers typically solve the problem by taking advantage of the fact that many components such as resistors and 
capacitors can be connected in configurations which result in them behaving together as if they were a single component with a different parameter value.
For example, two resistors with resistances A and B can be arranged in series to behave like a single resistor with equivalent resistance Req = Ra + Rb,
or in parallel to behave like a single resistor with equivalent resistance Req = 1 / ((1/Ra)+(1/Rb)). Capacitors work the same way, except the equations 
are swapped, with the aforementioned parallel relationship resulting from the capacitors physically connected in series and vice-versa.

Although manufacturers produce components like resistors and capacitors with many different values for their respective parameters, such diversity is expensive. 
As a result, the industry has settled on a few sets of standard parameter values which have been chosen because they allow engineers to construct a broad range 
of equivalent components from a small pool of parameter values actually embodied in real, physical ones. This works well in practice, largely thanks to the 
nature of the equations governing equivalent resistance and capacitance, since you can in theory produce an equivalent component with a parameter value of any 
rational number, even if you only have a bunch of base components with a single parameter value, so long as that value is rational and you can produce your 
equivalent with sufficiently many of them. You can even produce equivalent components with irrational equivalent parameter values, so long as the set of base
parameter values you're working from contains a value of any rational number times that irrational number. (On this note, One thing I personally think you 
should consider if you want to give this a shot is that relative to their inputs, one function is monatonically increasing and the other decreasing.)

In practice of course, engineers have to balance many tradeoffs in their designs, and reproducing an exact equivalent component with some theoretically derived 
ideal value for your application using an unlimited quantity of base components is generally less cost-effective than producing a close approximate using fewer,
so we often simply do that instead. This, however, introduces the additional wrinkle of choosing which approximate is best for the application, and how many
base components is it worth using to produce the desired equivalent. That's a much larger issue than it may sound, as the set of possible equivalents which
can be produced from a given number of components with parameter values chosen from a given set has a size with a factorial relationship to the number of 
available base values and the maximum number of actual base components with them we allow for use in producing our equivalent. Knowing how much closer using
an additional base component would make the approximation's equivalent value to the theoretical ideal is very important for making a good design decision, yet
it turns out that this is quite time-consuming to calculate.

In the past, I have attempted to automate doing this with a script I which calculates the set of possible equivalents and selects the best by brute force with
some minor optimizations, however as you may guess this approach is unacceptably inefficient for many scenarios. Another issue I ran into is that it's not enough
to calculate the possible values for the equivalent component, you also have to be able to tell the user how to construct it from the base components.

**The Problem:**

Given a array of double `baseResistances` representing available base resistance values, an integer `maxResistors` representing the maximum number of components 
you're allowed to use to produce an equivalent resistor, and a double `resistance` representing a theoretical ideal resistance, return a string which encodes in
**"serializable configuration format"** a **"configuration"** of base resistors that combine to behave as a equivalent resistor that is an **"optimal approximation"**.

An equivalent resistor is an **"optimal approximation"** if it satisfies all of the following two conditions for the given set of base values and maximum component count:
1. The difference between the equivalent's resistance and the ideal is the minimum value possible for any equivalent resistor satisfying the constraints.
2. The equivalent resistor is produced using the minimum number of base resistors possible out of any configuration producing that equivalent resistance value.

For example: given baseResistances = [2, 8], ideal resistance = 4.001, and max components = 2, the two possible equivalent resistors which could be considered to be
optimal approximations would be a 2 ohm in series with another 2 ohm, e.g. ((0)+(0)) in SCF, and an 8 ohm in parallel with another 8 ohm, e.g. ((1)//(1)) in SCF.
If the same inputs were given except the ideal was 2.001 instead, then the only optimal approximation would be to just use a single 2 ohm, e.g. (0) in SCF.

A **"configuration"** is a particular collection of components with specific parameter values and specific arrangement, thus resulting in the whole system behaving
as a single equivalent instance of that type of component with some equivalent parameter value equal to the result of composing the functions according to the
arrangement of the base components.

**"Serializable Configuration Format"** (or SCF) is a format for representing configurations of components as strings. SCF strings consist of a set of nested parentheses,
each representing an equivalent parameter value, as well as the symbol and inputs of the mathematical function which produces it, if applicable. These inputs are each 
their own set of nested parentheses, as they themselves represent parameter values encoded in SCF. An SCF string consisting solely of an integer between a single set of
parentheses represents a base component, particularly an instance of a base component with the parameter values of that at the corresponding index of the 
array of base components, e.g. baseResistances here. Otherwise, the interior of an SCF string consists of (for this example) two inputs separated by either '//' 
or '+', representing the resistor parallel and series configurations respectively. 

For example: given baseResistances = [1, 1.5, 2.7, 4.3, 4.7], the SCF string "((0)//(4))+((3)//(2))" represents an equivalent resistance of about 2.48313, constructed
by placing an equivalent resistance of about 0.824561 in series to an equivalent resistance of about 1.658571, where the 0.824561 is constructed by placing a base
resistor of 1 ohm in parallel with a base resistor of 4.7 ohms, and the 1.658571 is constructed by placing a base resistor of 4.3 ohms in parallel with a base 
resistor of 2.7 ohms.

**Example 1:**
<pre><strong>Input:</strong> baseResistances = [1, 5, 10], ideal resistance = 3.01, maxResistors = 3
<strong>Output:</strong> Either "((0)+(0))+(0)" or "(0)+((0)+(0))" will be accepted.
<strong>Explanation: </strong>It is valid use multiple base resistors of the same value.
This example is largely to clarify that you are not limited in how many VALUES you use out of those available for 
your base resistors, nor are you limited in how many base resistors you use of any given value so long as the total 
number of base resistors you use is equal to or below the value of maxResistors. 
As such, "(1)" is not an optimal approximation, since as shown above there exists a valid configuration of at most 
3 base resistors which produces an equivalent resistance (e.g. 3) which is closer to 3.01 ohms than the equivalent
resistance produced by the lone 5 ohm resistor the configuration "(1)" represents.

If you're still confused, please read Clarification 1.
</pre>


**Example 2:**
<pre><strong>Input:</strong> baseResistances = [10, 20], ideal resistance = pi*10, maxResistors = 5
<strong>Output:</strong> "((1)+((1)//((1)+((0)//(1)))))" or any synonymous SCF string will be accepted.
<strong>Explanation: </strong>This SCF string represents a configuration of base resistors with equivalent resistance around 3.142857,
the closest to pi*10 of any possible configuration of at most 5 resistors whose values can each be either 1 or 2 ohms.
Note: My unit tests directly compute the equivalent resistance represented by your output string, so SCF strings
representing analogous configurations all work if they use the same equivalent resistance and number of components.
</pre>


**Example 3:**
<pre><strong>Input:</strong> baseResistances = [1, 8], ideal resistance = 2.1, maxResistors = 4
<strong>Output:</strong> "(0)+(0)"
<strong>Explanation: </strong>Although you can use up to 3 resistors to produce an equivalent, the closest value possible is still 2,
which you only need two resistors i.e. 1 ohm in series with 1 ohm to produce it. While "((1)//(1))//((1)//(1))" still 
produces a 2 ohm equivalent resistance, this configuration does not meet condition #2 for qualifying as an optimal 
approximation as outlined above.
</pre>


**Constraints:**
<ul>
	<li><code>For this example, your solution needn't be extensible to components besides resistors. (1) </code></li>
	<li><code>Your solution may be within +/- 0.0001% of the unit test to account for variances due to floating point arithmetic.</code></li>
	<li><code>You can reliably assume that neither array sizes nor output string lengths will exceed Java's limits. </code></li>
	<li><code>Your code must be efficient enough (at a minimum!) to pass the included tests with the default heap size. </code></li>
</ul>

(1) For a followup question or an extra challenge of course, you're highly encouraged to try!

**Clarification 1:**
<pre>
As a mental image for pure software people, picture standing in front of a cabinet with one drawer for each entry in
the baseResistances array. Each drawer contains an infinite number of resistors, each resistor having 
the same resistance as all the others in its drawer, corresponding to that entry.
(i.e. [1, 5, 10] being a cabinet with 3 drawers, the 1st containing a bunch of 1 ohm resistors, 
the 2nd having a bunch of 5 ohm resistors, and the 3rd having a bunch of 10 ohm resistors.)
You are tasked with taking resistors from the cabinet (from any combination of the drawers)
and sticking them in a breadboard such that the equivalent resistance between two of the terminals is as close
to 3.01 ohms as you can, given the restrictions that you take at most 3, and only have access to the kinds of 
resistors which that cabinet has drawers for.
A "base" resistor is the real, physical object you can take from one of the drawers of the cabinet, 
while an "equivalent resistor" would be the little circuit you make out of them on the breadboard.
Since that little circuit electrically behaves as if it were just another kind of resistor with a different 
resistance value, including the fact that you can make even more elaborate equivalent resistors with them, 
you can create a wide variety of values by connecting a bunch of them in different ways.
The restriction in this problem is therefore on how many of those physical "base" resistors you use, 
not how many types of resistors, and not how many resistance values you use or generate intermediately.
</pre>
If you're purely a software person and somehow the description of this problem was challenging for you, please DM me.

I have zero clue how I can make this any simpler, so I'd like to hear how you'd describe this problem in your words instead.

