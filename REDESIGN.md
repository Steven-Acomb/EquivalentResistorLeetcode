# Redesign Notes (September 2026)

Written when the project came off the shelf for a review session. Read this before
touching anything else. The project stalled in February 2026 on a content question,
not an engineering one, and this document records the decision that resolves it.

## Why the project stalled

The original intent was for the problem to cover *every* way of wiring resistors
together. The implementation only covers **series-parallel** networks: SCF strings,
the `series()`/`parallel()` utilities, and the harness evaluator can only express
circuits that decompose recursively into series and parallel pairs. Those are exactly
the graphs with no K4 minor. Wheatstone bridges and other non-series-parallel
topologies produce resistance values no SCF string can reach. OEIS A048211
(series-parallel only) and A174283 (with bridges) diverge at 5 resistors.

A second, smaller premise also failed. The Stern-Brocot / Calkin-Wilf approach on the
`stephen_tree_solution` branch only produces linear chains, where each step adds one
resistor to the whole circuit. Branching trees that split the budget between two
sub-circuits can beat it: 19/17 needs 11 unit resistors as a chain but 10 as a tree
(test 8). No polynomial exact algorithm is known for the optimization problem in any
version below.

The full research notes, reading list, and ear-decomposition sketch live in
`solutions/equivalent-resistance/python/research_notes.md` on the unmerged
`origin/stephen_tree_solution` branch. Also on that branch: `config_explorer.py`
(enumerates all series-parallel values for n identical resistors, matches A048211)
and `stephen_tree_solution.py` (the CW-chain solver with the known-limitation comment).

## Decision

Ship **three problems as a ladder**, treated as two different kinds of thing:

| Version | Scope | Nature |
|---|---|---|
| V1 | Series-parallel, one base value | LeetCode-style, certifiable optimum, entry tier |
| V2 | Series-parallel, many base values | LeetCode-style, certifiable optimum, main human problem |
| V3 | Arbitrary networks, many base values | Open search problem, best coding-agent benchmark |

V1 and V2 share the same intended algorithm (V1 is a special case), so V1 exists for
two other reasons: it carries a literature-backed trap (continued fractions look
right and are wrong), and its achievable-value counts are checkable against OEIS.

V2 is what the repo already implements. Its statement must say explicitly that only
series-parallel networks are allowed and bridges are out of scope.

V3 is a multi-day project for a human, not a puzzle. Set expectations in the statement.

## Foundation fixes (do these first, all versions inherit them)

1. **Exact arithmetic for verification.** Base values become integers (ohms, or
   milliohms for E-series decimals). Expected answers are stored as exact fractions
   (`"p/q"`) in `testcases.json`. The harness evaluates the returned configuration
   with exact rationals (`fractions.Fraction` in Python, `BigInteger` pair in Java).
   Solvers may use floats internally. This removes the 0.0001% tolerance and the
   float-keyed dedup in the brute-force references, which can misrank candidates that
   differ in the last bit.
2. **Generate tests from an oracle, not by hand.** An exact brute-force oracle
   produces the expected answer for every instance and the adversarial cases:
   - budgets where the optimum uses fewer resistors than allowed (tiebreak check)
   - targets where the continued-fraction chain loses to a branching tree
   - sizes where a naive float brute force times out but exact DP with pruning passes
   - target 0 and target infinity
3. **Move reference solutions out of the tree solvers see.** `solutions/` currently
   ships the brute-force answers alongside the problem. Keep oracles on a private
   branch or separate repo. For a benchmark, the graded instance set must also be
   held back; publish only a sample set and the instance generator.
4. **Docker.** The engine's per-test limits use Linux-only calls (`resource`,
   `preexec_fn`, `/proc` polling) and do not run on Windows at all. Containerizing was
   the deferred Phase 2 item and is required for running untrusted agent code anyway.

## Intended solutions and test sizing

- **V1 / V2:** DP over resistor count with exact-fraction dedup, symmetry pruning
  (series and parallel are commutative; parallel is series under inversion), and
  value bounds. Size tests so this passes and a float-keyed brute force does not.
  That makes it a legitimate hard-tier problem with a known intended solution even
  though no polynomial algorithm exists.
- **V3:** needs three new pieces.
  - Output format: a netlist, a list of edges `(node_a, node_b, base_index)` with two
    designated terminal nodes. Dangling or zero-current resistors are legal but never
    optimal under the fewest-components tiebreak. Disconnected terminals evaluate to
    infinity.
  - Exact evaluator: solve Kirchhoff's equations by rational Gaussian elimination on
    the node-voltage system with a unit current injected at the terminals.
  - Oracle enumerator: 2-connected multigraphs with a distinguished battery edge, built
    by ear decomposition (see research notes). Dedup by resistance value, not by graph
    isomorphism; value dedup is sufficient for the optimization and much cheaper.
    The oracle will only certify optima for small resistor counts.
- Open question the V3 oracle will settle: whether any current V2 expected answers
  (test 8 in particular, 19/17 with 10 unit resistors) can be beaten on component
  count by a bridge. All current test targets are exactly achievable in
  series-parallel, so bridges cannot beat them on closeness.

## Benchmark design

The property that makes this family good for agent evaluation: **verification is
cheap and search is expensive.** The grader never trusts the agent's reasoning.

- **Two scoring tiers per version.** A certified tier where the oracle knows the
  optimum and scoring is pass/fail, and a heuristic tier of larger hidden instances
  scored by relative error against a frozen best-known value within a time budget,
  the way AtCoder heuristic contests work. The heuristic tier gives a continuous
  signal that separates strong agents from adequate ones.
- **Hidden instances from a seed.** Version the generator, not the instances.
- **Keep the traps.** The monotonicity hint and the Stern-Brocot literature lead
  toward the linear-chain approach. That is a feature.
- **Log more than pass/fail.** Wall time, memory, whether the agent built its own
  verifier, and which trap it fell into.
- The existing engine (inject solution, run in isolation, parse results) is already
  the right shape for a harness. The CLI is all a benchmark needs.

## What not to do

Do not resume the hosted workbench (apps.stephenacomb.com) until the problem content
above is settled. The workbench is a nice-to-have for friends; friends can clone the
repo. The project stalled on content, and more platform work will not unstick it.

## Task order when this comes off the shelf

1. Dockerize the engine (also fixes the Windows problem).
2. Convert V2 to integer inputs and exact-fraction verification in both harnesses.
3. Write the exact V2 oracle (private branch) and regenerate `testcases.json` from it,
   including adversarial cases.
4. Split out V1 as its own problem directory with a short statement and OEIS-checked
   oracle.
5. Rewrite the V2 statement: series-parallel only, bridges out of scope.
6. V3: netlist format, exact evaluator, ear-decomposition enumerator, small certified
   test set, heuristic tier.
7. Benchmark packaging: instance generator, hidden sets, scoring script, logging.

## Repo state at time of writing

- `main` last substantive commit: 2026-02-14. Working tree clean apart from this file.
- Remote branches: `stephen_tree_solution` (notes and CW solver, 2026-02-15, unmerged),
  `claude_solution_attempt` (empty, points at main),
  `Naive-Brute-Force-Implementation-Testing` (pre-restructure, historical).
- Phases 0 through 3.5 in ROADMAP.md are done. Phases 4 and 5 were never started and
  are superseded by the task order above.
- This machine: Python 3.13, JDK 17, no Maven. Engine does not import on Windows.
