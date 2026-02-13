# Acid Test Report: Claude Code Brute-Force Attempt (Java)

## Context

Fresh session with no prior context (CLAUDE.md deleted, MEMORY.md empty). Goal: read the README, understand the problem, implement a brute-force solution in Java, and run the tests — using only what the repo provides.

## User Experience

### What worked well

- **README was self-contained.** The problem statement, SCF format spec, utility docs, file paths, and run instructions were all in one place. No clarifying questions needed about the core problem.
- **Examples were helpful.** The three worked examples (especially Example 3 showing the tiebreak rule) made the optimization criteria unambiguous for finite targets.
- **Utility functions were well-documented.** The table of `series`, `parallel`, `baseScf`, `combineScf`, and `evaluateConfig` with examples made it easy to build SCF strings programmatically.
- **Solution stub had clear imports and method signature.** Opening `Solution.java` immediately showed the interface contract and available utilities.
- **Project structure section** made it trivial to find every relevant file.
- **Tests were runnable out of the box** with `mvn test`. No setup friction beyond standard JDK + Maven prerequisites.
- **Execution engine `-s` flag** provides a clean workflow for testing solution files stored outside the harness directory (e.g., a brute-force reference in `examples/`) without overwriting `Solution.java`.

### Friction

- **`Double.MAX_VALUE` / infinity target behavior is unclear.** The README says: *"When resistance is infinity... your goal is to maximize the equivalent resistance."* But tests 5-8 expect values far below the achievable maximum (see detailed results below). This was the single biggest source of confusion — I implemented "maximize resistance" as stated, and tests 5-8 all failed. See [Tests 5-8 Analysis](#tests-5-8-analysis) for details.
- **Test ordering.** Test 1 is the hardest case (151 base values, max 4 resistors) and runs first. Since it OOMs for brute-force solutions, the `POINTS` counter and test output are harder to parse. Consider reordering so simpler tests run first, or note in the README that test 1 is expected to challenge brute-force approaches.
- **No per-test timeout.** Maven Surefire's default timeout is effectively unlimited. For brute-force attempts that may hang on large inputs, a configured per-test timeout would provide cleaner feedback than an OOM crash.

---

## Test Results

### Passing (3/8)

| Test | Base resistances | Target | Max | Result |
|------|-----------------|--------|-----|--------|
| 2 | [1, 2] | ~3.1429 (22/7) | 5 | PASS — found `(1)+((1)//((1)+((0)//(1))))` |
| 3 | [1, 1000] | 0 | 8 | PASS — found 8× parallel 1-ohm = 0.125 |
| 4 | [0.1, 1] | MAX | 8 | PASS — found 8× series 1-ohm = 8.0 |

### Failing (5/8)

| Test | Base resistances | Target | Max | Expected | Got | Reason |
|------|-----------------|--------|-----|----------|-----|--------|
| 1 | E96 series (151 values) | ~2.483 | 4 | ~2.483 | OOM | dp[3] ≈ 13.6M entries; dp[4] would need ~4B pair iterations |
| 5 | 35 custom values | MAX | 3 | 3733.33 | 25200 | My solution maximizes (3×8400 series); test expects a smaller value |
| 6 | [1680] | MAX | 8 | 3733.33 | 13440 | My solution maximizes (8×1680 series); test expects 11200/3 |
| 7 | [13] | MAX | 13 | 1.0 | 169 | My solution maximizes (13×13 series); test expects 13÷13 parallel = 1 |
| 8 | [17] | MAX | 10 | 19.0 | 170 | My solution maximizes (10×17 series); test expects 19 |

---

## Tests 5-8 Analysis

Tests 5-8 all pass `Double.MAX_VALUE` as the target resistance. Per the README, this means "maximize the equivalent resistance." My brute-force correctly finds the all-series maximum in each case:

- **Test 7** (base=[13], max=13): 13 resistors in series = 13×13 = 169 ohms. But the test expects 1 ohm (13 resistors in parallel = 13/13). 169 > 1, so the all-series config is unambiguously the maximum.
- **Test 8** (base=[17], max=10): 10 in series = 170 ohms. Test expects 19 ohms.
- **Test 6** (base=[1680], max=8): 8 in series = 13440 ohms. Test expects 11200/3 ≈ 3733.33 ohms.
- **Test 5** (35 values up to 8400, max=3): 3×8400 = 25200. Test expects 3733.33.

**Conclusion:** The expected values for tests 5-8 are inconsistent with the README's definition of "maximize." These tests likely need reworked expected values, or the README needs to clarify a different interpretation of the MAX target.

Note that **test 4 passes** with the "maximize" interpretation — base=[0.1, 1], max=8, expected=8 (8×1 in series), which IS the maximum. So the MAX behavior is correct for test 4 but not for 5-8.

---

## Test 1 Analysis

Test 1 uses the E96 standard resistor series (151 values) with max 4 components. This is computationally expensive for brute force:

| dp level | Entries | Pair iterations to build |
|----------|---------|------------------------|
| dp[1] | 151 | — |
| dp[2] | ~45,000 | 151 × 151 × 2 |
| dp[3] | ~13,600,000 | 151 × 45k × 2 |
| dp[4] | would need ~4,000,000,000 pair iterations | infeasible |

The solution OOMs at dp[3] due to HashMap overhead. This is a legitimate brute-force limitation — solving it efficiently likely requires pruning (beam search), sorted-array binary search, or mathematical insight about which base values to consider.

**Recommendation:** Keep test 1 as a case that explicitly challenges brute-force solutions. Consider documenting that test 1 is expected to require optimization beyond naive enumeration, so users know it's intentionally hard.

---

## Brute-Force Implementation

The brute-force solution is saved at `user_stories/java_test/examples/brute_force_java.java`. It can be tested via the execution engine without overwriting `Solution.java`:

```bash
python3 -m engine run -p equivalent-resistance -l java -s user_stories/java_test/examples/brute_force_java.java
```

### Approach

Dynamic programming over component count:
1. `dp[1]` = all base resistors (value -> Config tree node)
2. `dp[n]` = all values from combining `dp[i] × dp[n-i]` via series and parallel, for `i` in `1..n/2`
3. Track overall best: closest to target (or largest for MAX), with fewest components as tiebreaker
4. Convert winning Config tree to SCF string at the end

Uses a lightweight `Config` tree (leaf = base index, internal = left + right + operation) to avoid storing SCF strings during search. SCF is generated only for the final answer.
