# Acid Test Report: Claude Code Brute-Force Attempt

## Context

Fresh session with no prior context (CLAUDE.md deleted, MEMORY.md empty). Goal: read the README, understand the problem, implement a brute-force solution in Python, and run the tests — using only what the repo provides.

## User Experience

### What worked well

- **README was self-contained.** The problem statement, SCF format spec, utility docs, file paths, and run instructions were all in one place. I never needed to ask a clarifying question about the problem itself.
- **Examples were helpful.** The three worked examples (especially Example 3 showing the tiebreak rule) made the optimization criteria unambiguous.
- **Utility functions were well-documented.** The table of `series`, `parallel`, `base_scf`, `combine_scf`, and `evaluate_config` with examples made it easy to build SCF strings programmatically without reverse-engineering the format.
- **Solution stub had clear imports.** Opening `solution.py` immediately showed what was available — no guessing about module names or import paths.
- **Project structure section** made it trivial to find every relevant file.
- **Tests were runnable out of the box** with just `pytest -v` (after `cd` to the python directory). No setup friction.
- **Execution engine `-s` flag works as designed.** The brute-force reference was placed in `examples/brute_force_python.py` (outside the harness directory), and the engine correctly injected it into a temp copy of the harness and ran the tests — without touching `solution.py`. This validates the engine's intended workflow for testing arbitrary solution files.

### Minor friction

- **No `pytest-timeout` installed.** The `requirements.txt` doesn't include it, so `--timeout` flag isn't available. The README says "within the default timeout" without specifying what that timeout is or how it's enforced. For brute-force attempts that may hang on large inputs, having a per-test timeout mechanism would help (see recommendations below).
- **Test ordering.** Test 1 is the hardest case (151 base values, max 4 resistors) and runs first. Since it hangs/OOMs for brute-force solutions, you can't see results for the easier tests without `-k` filtering. Consider reordering so simpler tests run first.

---

## Test Results

### Passing (3/8)

| Test | Base resistances | Target | Max | Result |
|------|-----------------|--------|-----|--------|
| 2 | [1, 2] | ~3.1429 | 5 | PASS |
| 3 | [1, 1000] | 0 | 8 | PASS |
| 4 | [0.1, 1] | inf | 8 | PASS |

### OOM crash (1/8)

| Test | Issue |
|------|-------|
| 1 | 151 base values with max_resistors=4 causes combinatorial explosion at DP level 3 (~13M entries). The process gets OOM-killed before the engine's 120s timeout fires. |

### Failing — incorrect expected values (4/8)

Tests 5-8 all pass `float("inf")` as the target (meaning "maximize resistance") but assert against expected values that are far below the achievable maximum.

#### Test 5
- **Base:** 35 values (max value 8400), **max_resistors:** 3
- **Expected:** 11200/3 = 3733.33
- **Achievable max:** 8400 + 8400 + 8400 = 25200
- **Issue:** Expected value is less than a single base resistor (8400 > 3733)

#### Test 6
- **Base:** [1680], **max_resistors:** 8
- **Expected:** 11200/3 = 3733.33
- **Achievable max:** 1680 * 8 = 13440
- **Issue:** Expected = 1680 * 20/9, not achievable as a maximum

#### Test 7
- **Base:** [13], **max_resistors:** 13
- **Expected:** 1
- **Achievable max:** 13 * 13 = 169
- **Issue:** Expected value (1 = 13/13) is the *minimum* (all parallel), not the maximum

#### Test 8
- **Base:** [17], **max_resistors:** 10
- **Expected:** 19
- **Achievable max:** 17 * 10 = 170
- **Issue:** 19 is not achievable as a maximum with any series/parallel combination of 17-ohm resistors

#### Likely cause
These tests appear to have been written with specific finite target values in mind, but `float("inf")` was passed as the resistance argument instead. For example, test 6 probably intended `target=3733.33` (approximate 11200/3 using only 1680-ohm resistors), which would be a legitimate and interesting test case.

#### Recommendation
Replace the `float("inf")` in tests 5-8 with the intended finite target values, or write new test cases entirely.

---

## Execution Engine Findings

### The `-s` injection workflow works

Running the brute-force reference from `examples/` via the engine:

```bash
python3 -m engine run -p equivalent-resistance -l python -s examples/brute_force_python.py
```

The engine correctly:
1. Copied the Python harness to a temp directory
2. Injected the brute-force solution file over `solution.py`
3. Ran `pytest --junitxml=results.xml -v`
4. Cleaned up the temp directory afterward

This confirms users can keep multiple solution attempts anywhere on disk and test them without modifying the repo.

### Failure mode could be cleaner

When the brute force OOM'd on test 1, the engine reported:

```
EQUIVALENT-RESISTANCE (python) -- BUILD ERROR

  Killed
```

Issues:
- **"BUILD ERROR" is misleading.** The code built and started running fine — it was killed at runtime by the OOM killer. The engine classifies this as a build error because no JUnit XML was produced, but the actual cause is very different.
- **No per-test isolation.** Because pytest runs all tests in a single process, the OOM on test 1 kills the entire suite. Tests 2-4 (which would pass) never get a chance to run.
- **No timeout on individual tests.** The engine has a 120s timeout on the whole subprocess, but the OOM kill fires before the timeout. Adding `pytest-timeout` to requirements and a per-test timeout (e.g., 30s) would let slow tests fail individually with `TIMEOUT` rather than crashing the whole run.

### Recommendations for the engine

1. **Detect signal-based kills.** If the subprocess exits with signal 9 (SIGKILL/OOM), report `RUNTIME ERROR (process killed — likely out of memory)` instead of `BUILD ERROR`.
2. **Add `pytest-timeout` to the Python harness.** Include it in `requirements.txt` and add `--timeout=30` (or similar) to the test command in `runner.json`. This gives per-test timeouts so easy tests can still pass even if a hard test hangs.
3. **Reorder tests.** Put the 151-value case last so users see passing results before the hard case fails.

---

## Design Discussion: Including a Brute-Force Reference

### Goal
Ship a working brute-force implementation per language that:
- Gives users a readable baseline to learn from
- Demonstrates how the utilities, SCF format, and test harness work together
- **Explicitly fails** on the hard test case(s) to motivate optimization

### Where it lives
`examples/brute_force_python.py` (and equivalents for other languages). Users run it through the engine's `-s` flag — no conflict with the blank `solution.py` stub.

### How it should fail
Currently it OOM-crashes, which is ugly. With per-test timeouts, it would instead:
- **Pass** tests 2-4 (and replacements for 5-8) — the small/medium cases
- **TIMEOUT** on the 151-value case — a clear, intentional signal that brute force isn't enough

This gives the ideal pedagogical arc: "here's a correct approach that works on small inputs; your job is to make it scale."

### Test design for the hard case
The 151-value test (current test 1) should be:
- **Moved to the end** of the test suite so it runs last
- **Documented** in the README as a challenge case that brute force is not expected to pass
- Optionally marked with `@pytest.mark.challenge` or similar for easy filtering

---

## Solution Approach (brute-force DP)

Reference implementation at `examples/brute_force_python.py`:

1. **Level 1:** Each base resistor as a single-component configuration.
2. **Level n:** For each split i + j = n (i <= j), combine every config from level i with every config from level j using both series and parallel. Store results in a dict keyed by resistance value to deduplicate.
3. **Selection:** Across all levels, pick the configuration closest to target, breaking ties by fewest components.

This is correct and passes all well-formed tests with small inputs. The main limitation is combinatorial growth when both the base set and max_resistors are large — O(B^n) where B is the number of base values and n is max_resistors.

## Other Notes from Human
- LLM coding agent did not seem to understand the execution engine method for running tests and initially went with just modifying solution.py until it found that clunky and I asked it to check the readme again. We should probably consider whether we want to clarify how that works and list that as a preferred method up front or not in the readme. =
