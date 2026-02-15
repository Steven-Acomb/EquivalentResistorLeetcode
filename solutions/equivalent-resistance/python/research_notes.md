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

### Two fundamentally different configuration spaces

There are two levels to this problem that must not be conflated:

1. **Series-parallel configurations** — circuits that can be recursively decomposed into two
   sub-circuits combined with series or parallel. These are exactly the circuits representable as
   binary trees (and expressible in SCF format). The recursive decomposition IS the definition of
   series-parallel, so `config_explorer.py`'s recursive enumeration is provably complete for this
   class.

2. **General configurations** — arbitrary 2-connected graphs with resistors as edges. This
   includes bridges (Wheatstone bridge, etc.) and other topologies that have no series-parallel
   decomposition. A graph is series-parallel if and only if it has no K4 (complete graph on 4
   nodes) as a minor. Graphs with K4 minors require Kirchhoff's laws or delta-wye transforms to
   evaluate — `series()` and `parallel()` cannot express them.

Enumerating all series-parallel topologies is straightforward (recursive construction). Enumerating
all general topologies is a significantly harder graph theory problem — you can't just recurse on
sub-circuits because non-series-parallel graphs don't decompose that way.
See [Gottlieb/Karnofsky](https://cs.nyu.edu/~gottlieb/tr/overflow/2003-oct-3-more.html) for
discussion.

### Defining the general topology space (work in progress)

Karnofsky's formulation models each resistor as an edge and adds a distinguished "battery" edge
connecting the two terminals. This turns any valid resistor network into a 2-connected graph: even
a simple series chain becomes 2-connected once the battery edge closes the loop. In this model, a
network of n resistors = a 2-connected graph on n+1 edges with one distinguished (battery) edge.

This must be a **multigraph** (allowing multiple edges between the same vertex pair), since
parallel resistors sharing both endpoints are multiple edges between two nodes.

So the candidate enumeration space is: **all 2-connected multigraphs on n+1 edges, with one
distinguished edge, up to isomorphism preserving the distinguished edge.**

*This definition is still a work in progress — it's not yet clear whether this is exactly the
right formulation or whether additional constraints are needed. More reading and thought required.*

### Ear decomposition: building general topologies edge-first

A key awkwardness of this problem: resistors (edges) are the primary objects, but graph theory
usually treats nodes as primary and edges as relationships between them. Here, junctions (nodes)
are emergent — when you add a resistor, you might connect two existing junctions or create new
ones. The number of nodes depends on where you put the resistors.

Graph theory's answer to this is the **ear decomposition** (Whitney's theorem): every 2-connected
graph can be built by starting with a cycle and repeatedly adding **ears** — paths that start and
end at existing nodes, with zero or more new intermediate nodes.

**Construction for resistor networks:**
1. Start with a cycle: the battery edge + one resistor between A and B (2 nodes, 2 edges)
2. Repeatedly add ears. An ear of length k adds **k edges** (resistors) and **k-1 new nodes**
   (junctions):
   - Length 1: edge between two existing nodes, no new nodes (parallel-type addition)
   - Length 2: one new node connected to two existing nodes
   - Length 3+: chain of new nodes bridging two existing ones

**Connection to series-parallel:** If you only add ears between endpoints of existing edges, or
subdivide existing edges, you stay in series-parallel territory. The moment you add an ear
connecting two nodes that aren't endpoints of the same edge — like bridging M1 to M2 in the
Wheatstone bridge — you leave it. This is the operation that series-parallel decomposition can't
represent.

**Wheatstone bridge via ear decomposition:**
1. Start: cycle of length 3: A-M1-B-A (edges: A-M1, M1-B, A-B battery). 3 edges, 3 nodes.
2. Ear length 2 from A to B via M2: adds A-M2, M2-B. 5 edges, 4 nodes.
3. Ear length 1 from M1 to M2: the bridge resistor. 6 edges total (5 resistors + battery). Done.

Step 3 is what makes it non-series-parallel — it connects two internal nodes (M1, M2) that aren't
endpoints of the same existing edge. This is the operation that series-parallel decomposition
can't represent.

**Enumeration via ears:** To enumerate all topologies with n resistors, systematically generate all
sequences of ear additions that total n+1 edges (n resistors + battery). At each step, choose
which pair of existing nodes to attach the ear to and how long to make it. Whitney's theorem
guarantees completeness: every 2-connected graph has at least one ear decomposition, so every
topology will appear. Different ear sequences can produce the same graph, so deduplication (by
graph isomorphism preserving the battery edge) is needed.

### Walkthrough: all topologies for n ≤ 3

Enumerated by trying all initial cycle lengths and ear additions, deduplicating by isomorphism.

**n=1 (2 total edges):**

Only possibility: cycle of length 2 (A-B battery, A-B resistor). **1 topology.**

| Topology | Edges | Value (1Ω) | Description |
|----------|-------|-----------|-------------|
| 1 | A-B(bat), A-B | 1 | Single resistor |

**n=2 (3 total edges):**

- Cycle 2 + ear 1 (A→B): three parallel edges. Two resistors in parallel.
- Cycle 3 (A-M-B-A): triangle with battery on A-B. Two resistors in series.

**2 topologies**, both series-parallel.

| Topology | Edges | Value (1Ω) | Description |
|----------|-------|-----------|-------------|
| 1 | A-B(bat), A-B, A-B | 1/2 | Two parallel |
| 2 | A-B(bat), A-M, M-B | 2 | Two series |

**n=3 (4 total edges):**

- **Cycle 2 + two ears of length 1** (A→B, A→B): four parallel A-B edges.
  = three resistors in parallel.

- **Cycle 2 + ear of length 2** (A→M→B): edges A-B(bat), A-B, A-M, M-B.
  = R // (R+R). One resistor parallel with two in series.
  *(Same graph reached by: cycle 3 (A-M-B-A) + ear 1 (A→B). Duplicate.)*

- **Cycle 3 + ear of length 1** (A→M): edges A-B(bat), A-M, A-M, M-B.
  = (R//R) + R. Parallel pair in series with one.
  *(Ear M→B gives isomorphic graph — swap A↔B, battery is undirected. Duplicate.)*

- **Cycle 4** (A-M1-M2-B-A): edges A-B(bat), A-M1, M1-M2, M2-B.
  = three resistors in series.

5+ nodes impossible (4 edges, average degree < 2, can't be 2-connected).

**4 topologies**, all series-parallel. Matches config_explorer output exactly.

| # | Construction | Value (1Ω) | Description |
|---|-------------|-----------|-------------|
| 1 | Cycle 2 + ear 1 + ear 1 | 1/3 | Three parallel |
| 2 | Cycle 3 + ear 1 (A-M) | 3/2 | (R//R) + R |
| 3 | Cycle 2 + ear 2 | 2/3 | R // (R+R) |
| 4 | Cycle 4 | 3 | Three series |

All four are series-parallel, as expected — non-series-parallel topologies first appear at n=5
(Wheatstone bridge requires 5 resistors + battery = 6 edges, 4 nodes).

### Series-parallel counts (from config_explorer.py)

For n identical 1-ohm resistors (series-parallel only):

| n  | topologies (upper bound) | distinct values | cumulative values |
|----|-------------------------|-----------------|-------------------|
| 1  | 1                       | 1               | 1                 |
| 2  | 2                       | 2               | 3                 |
| 3  | 8                       | 4               | 7                 |
| 4  | 40                      | 9               | 15                |
| 5  | 224                     | 24              | 37                |
| 6  | 1344                    | 55              | 83                |
| 7  | 8448                    | 147             | 205               |
| 8  | 54912                   | 384             | 502               |
| 9  | 366080                  | 995             | 1234              |
| 10 | 2489344                 | 2618            | 3081              |

- "Topologies (upper bound)" counts ordered labeled binary trees — overcounts because it treats
  `series(A, B)` and `series(B, A)` as distinct. True structurally distinct count is lower.
- "Distinct values" is the real count — deduplicated by resistance value. Matches OEIS A048211.
- Topologies grow ~4^n; distinct values grow ~2.55^n.

### Where they diverge

The general case (A174283) first diverges from series-parallel (A048211) at n=5, where bridge
configurations add 1 extra achievable resistance value. The gap grows with n. The smallest
non-planar circuit requires 8 resistors.

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

## Computational Complexity: What's Known

### The short answer
**There is no published formal complexity classification for this exact problem.** The specific
question — "given a target resistance, a set of base values, and a budget n, find the
series-parallel configuration of at most n resistors that minimizes the approximation error" — does
not appear in the complexity theory literature. It is an open question.

### Evidence it's hard
- The configuration space grows exponentially (~2.55^n for distinct values, ~4^n for topologies).
- Several closely related graph resistance optimization problems ARE proven NP-hard:
  - Network design for s-t effective resistance (Chan et al. 2022)
  - Optimal node elimination ordering in resistor networks
  - Minimizing total effective graph resistance by adding links

### Evidence there's exploitable structure
- Continued fractions provide a polynomial-time heuristic that often works well (the SB/CW
  approach we built). Khan (2014) explicitly connects unit resistor ladder networks to CF
  approximation.
- Fibonacci numbers bound the achievable rationals: for n unit resistors, any achievable p/q has
  p, q ≤ F(n+1) ≈ φ^n (Khan 2010).
- **Chan et al. (2022) found an FPTAS** (fully polynomial-time approximation scheme) for the
  network design variant specifically on **series-parallel graphs**. So the series-parallel
  restriction does make things more tractable.
- The Farey sequence / Stern-Brocot / continued fraction connections are real and used in the
  literature (Khan 2012, Isokawa 2016).

### The most relevant paper
Johnson & Walters, "Optimal Resistor Networks" (2022) appears to directly address the question of
which resistance values can be achieved optimally with n resistors and how to find them.

### Bottom line
The instinct that "something this structured shouldn't be NP-hard" has legitimate support — the
series-parallel case has exploitable structure (FPTAS exists for a related formulation, continued
fractions give efficient heuristics, Fibonacci bounds constrain the search space). But nobody has
proven it either way for the exact optimization problem. This may be genuinely at the frontier.

---

## Open Questions
- Is there an efficient algorithm for the series-parallel case that handles branching?
- For the general (non-series-parallel) case, how would the output format work? (Adjacency list?
  Netlist? SPICE format?)
- How much do bridge configurations actually help in practice? (A174283 shows only 1 extra value
  at n=5, 4 extra at n=6 — is it worth the complexity?)
- Is the exact optimization problem (minimize approximation error with fewest components)
  NP-hard, or does the series-parallel structure make it polynomial? Open question.

---

## Reading List

### Foundational / Enumeration
- MacMahon, "The combinations of resistances," *The Electrician* 28, pp. 601-602, 1892.
  Reprinted in *Discrete Applied Mathematics* 54, pp. 225-228, 1994.
- Riordan & Shannon, "The number of two-terminal series-parallel networks," *J. Math. Physics*
  21, pp. 83-93, 1942.
  [PDF via OEIS](https://oeis.org/A000084/a000084_1.pdf)

### Bounds and Structure of Achievable Values
- Amengual, "The intriguing properties of the equivalent resistances of n equal resistors
  combined in series and in parallel," *Am. J. Physics* 68(2), pp. 175-179, 2000.
  [ADS](https://ui.adsabs.harvard.edu/abs/2000AmJPh..68..175A/abstract)
- Khan, "The bounds of the set of equivalent resistances of n equal resistors combined in series
  and in parallel," 2010.
  [arXiv:1004.3346](https://arxiv.org/abs/1004.3346)
- Khan, "Farey sequences and resistor networks," *Proc. Indian Acad. Sci.* 122(2), pp. 153-162,
  2012.
  [ResearchGate](https://www.researchgate.net/publication/45912866)
- Khan, "Rational and irrational numbers from unit resistors," *Eur. J. Phys.* 35, 015008, 2014.
  [ADS](https://ui.adsabs.harvard.edu/abs/2014EJPh...35a5008K/abstract)

### Continued Fractions and Resistor Networks
- Isokawa, "Series-parallel circuits and continued fractions," *Applied Mathematical Sciences*
  10(25-28), 2016.
  [PDF](https://www.m-hikari.com/ams/ams-2016/ams-25-28-2016/p/isokawaAMS25-28-2016.pdf)

### Bridge / Non-Series-Parallel Configurations
- Stampfli, "Bridged graphs, circuits and Fibonacci numbers," *Appl. Math. Comput.* 302,
  pp. 68-79, 2017.
- Deilami & Zhelyabovskyy, "On the Average Resistance of n-circuits," 2024.
  [arXiv:2410.07261](https://arxiv.org/abs/2410.07261)

### Complexity of Related Problems
- Chan, Lau, Schild, Wong & Zhou, "Network design for s-t effective resistance," *ACM Trans.
  Algorithms*, 2022. General case NP-hard; FPTAS for series-parallel graphs.
  [arXiv:1904.03219](https://arxiv.org/abs/1904.03219)
- "Minimizing the effective graph resistance by adding links is NP-hard," 2023.
  [arXiv:2302.12628](https://arxiv.org/abs/2302.12628)

### Directly Relevant
- Johnson & Walters, "Optimal Resistor Networks," 2022.
  [arXiv:2206.08095](https://arxiv.org/abs/2206.08095)

### Tools
- synthres — resistance synthesis tool (brute-force enumeration via integer partitions).
  [GitHub: kwantam/synthres](https://github.com/kwantam/synthres)

### OEIS Sequences
- [A000084](https://oeis.org/A000084) — number of series-parallel networks with n edges
- [A048211](https://oeis.org/A048211) — distinct resistances, n identical resistors, series-parallel only
- [A174283](https://oeis.org/A174283) — distinct resistances, n identical resistors, including bridges
- [A337516](https://oeis.org/A337516) — distinct resistances, general configurations (bridge + fork)
