# Research Notes: Equivalent Resistance Problem

## The Stern-Brocot / Calkin-Wilf Approach

### Core Idea
For the single-base-resistance case, normalize the target: `target / base_resistance` gives a
rational number to approximate. Then:

1. **Stern-Brocot search** — The SB tree is a BST over all positive rationals. Binary search to
   depth `max_resistors` finds the closest rational within the budget. O(n) time.
2. **SB → CW conversion** — The Stern-Brocot and Calkin-Wilf trees contain the same fractions at
   each level (same depth for any given fraction). Converting between them is done by reversing
   the L/R path (equivalently, reversing the continued fraction representation).
3. **CW path → SCF** — The Calkin-Wilf tree path directly encodes a construction: left = parallel
   with a base resistor, right = series with a base resistor. Walk the path to build the SCF string.

### Key Limitation: Linear Chains Only
The CW path only produces **linear chain** (caterpillar) configurations — each step combines the
*entire* previous circuit with one new base resistor. The problem allows **tree-shaped**
configurations that split the resistor budget between two independent sub-circuits.

**Example:** `19/17` has continued fraction `[1, 8, 2]`, sum = 11, so a CW chain needs 11 resistors.
But a branching configuration achieves it in 10 by splitting into two sub-circuits:
- Left: `parallel(17, 17) = 8.5` (2 resistors, CW depth 2)
- Right: nested series/parallel structure = 10.5 (8 resistors, CW depth 8)
- Combined: `series(8.5, 10.5) = 19.0`

Both sub-circuits are themselves linear CW chains — the branching only happens at the join point.
The algorithm passes tests where the optimal is a linear chain but fails when branching is needed.

### References
- [Stern-Brocot tree (Wikipedia)](https://en.wikipedia.org/wiki/Stern%E2%80%93Brocot_tree)
- [Calkin-Wilf tree (Wikipedia)](https://en.wikipedia.org/wiki/Calkin%E2%80%93Wilf_tree)
- The same numbers appear at the same levels in both trees. One tree can be obtained from the other
  by a bit-reversal permutation on the numbers at each level, or equivalently by reversing the
  continued fraction representations.

---

## Configuration Space: How Big Is It?

For n identical 1-ohm resistors (series-parallel only):

| n  | topologies | distinct values | cumulative values |
|----|-----------|-----------------|-------------------|
| 1  | 1         | 1               | 1                 |
| 2  | 2         | 2               | 3                 |
| 3  | 8         | 4               | 7                 |
| 4  | 40        | 9               | 15                |
| 5  | 224       | 24              | 37                |
| 6  | 1344      | 55              | 83                |
| 7  | 8448      | 147             | 205               |
| 8  | 54912     | 384             | 502               |
| 9  | 366080    | 995             | 1234              |
| 10 | 2489344   | 2618            | 3081              |

- Topologies grow ~4^n (number of full binary trees with n leaves × 2 operator choices per node).
- Distinct values grow much slower due to commutativity and value collisions.
- OEIS A048211: distinct resistances from n identical resistors, series-parallel only.

---

## PROBLEM DESIGN ISSUE: Bridge / Non-Series-Parallel Configurations

**The current problem setup (SCF format, series/parallel only) does not capture all possible
resistor configurations.** Circuits like the Wheatstone bridge cannot be decomposed into nested
series and parallel operations — they require Kirchhoff's laws or delta-wye transforms to solve.

### What's missing
- **Bridge (Wheatstone) configurations** — a resistor connecting midpoints of two parallel
  branches. Minimum 5 resistors. Cannot be expressed in SCF.
- **More general non-series-parallel topologies** — any circuit graph that isn't a series-parallel
  graph. These produce resistance values unreachable by any series-parallel combination.

### Relevant OEIS sequences
- **A048211** — distinct resistances from n identical resistors, series-parallel only (what the
  current problem covers)
- **A174283** — distinct resistances from n identical resistors, including bridge configurations.
  Diverges from A048211 at n=5 (bridge circuits need ≥5 resistors).
- **A337516** — related sequence for general configurations including "bridge or fork" topologies.

### Impact on the problem
The original intent was for the problem to cover **all** possible configurations of resistors, not
just series-parallel ones. The current design (SCF format for output, `series()`/`parallel()` as
the only utility functions, and test harness evaluation via SCF parsing) fundamentally restricts
solutions to the series-parallel subset.

**This may require reworking:**
- The output format (SCF can only represent series-parallel circuits)
- The utility library (would need general circuit evaluation, not just series/parallel)
- The test cases and expected outputs (some optimal configurations might be non-series-parallel)
- The problem statement (currently only defines series and parallel)

Alternatively, the problem could be explicitly scoped to series-parallel configurations only,
which is still a rich and challenging optimization problem. This would need to be made clear in the
problem statement.

---

## Open Questions
- Is there an efficient algorithm for the series-parallel case that handles branching?
- For the general (non-series-parallel) case, how would the output format work? (Adjacency list?
  Netlist? SPICE format?)
- How much do bridge configurations actually help in practice? (A174283 shows only 1 extra value
  at n=5, 4 extra at n=6 — is it worth the complexity?)
