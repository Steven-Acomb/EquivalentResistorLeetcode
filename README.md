# Equivalent Resistor Leetcode

A custom leetcode-style coding challenge platform, starting with an electrical engineering optimization problem.

## The Problem

When designing circuits, engineers often can't find a single resistor with the exact value they need. Instead, they combine resistors in **series** and **parallel** to approximate a target value:

- **Series**: `Req = Ra + Rb` (resistances add)
- **Parallel**: `Req = 1 / ((1/Ra) + (1/Rb))` (resistances combine inversely)

These combinations nest — you can put a series pair in parallel with another resistor, and so on. With enough components, you can approximate any target resistance, but finding the *best* combination is computationally hard.

### Your task

Write a function that, given:

| Parameter | Type | Description |
|-----------|------|-------------|
| `baseResistances` | array of floats | Available resistor values (you have unlimited copies of each) |
| `resistance` | float | Target resistance to approximate (may be `infinity` / `Double.MAX_VALUE`) |
| `maxResistors` | int | Maximum number of components you can use |

...returns a string in **SCF format** (described below) representing the resistor configuration that is the **optimal approximation** of the target.

### What "optimal" means

Your configuration must satisfy two conditions (in priority order):

1. **Closest value**: The equivalent resistance is as close to the target as possible.
2. **Fewest components**: Among all configurations that achieve that closest value, yours uses the fewest total resistors (counting each physical resistor, not distinct values — two 1-ohm resistors counts as 2).

### SCF (Serializable Configuration Format)

The whole point of this problem is to tell an engineer *how to wire up the resistors* — not just the target value, but which resistors to use and how to connect them. SCF is a string format that encodes exactly that: the structure and components of a resistor configuration, so someone could read it and build the circuit.

| SCF string | Meaning |
|------------|---------|
| `0` | A single base resistor — the one at index 0 of `baseResistances` |
| `3` | A single base resistor at index 3 |
| `(0)+(1)` | Index 0 in **series** with index 1 |
| `(0)//(1)` | Index 0 in **parallel** with index 1 |
| `((0)//(4))+((3)//(2))` | A series combination of two parallel pairs |

The two operators are `+` (series) and `//` (parallel). Nesting builds up complex configurations — the test harness evaluates your SCF string to compute the resulting equivalent resistance.

**Example**: Given `baseResistances = [1, 1.5, 2.7, 4.3, 4.7]`, the SCF string `((0)//(4))+((3)//(2))` means: put a 1-ohm resistor (index 0) in parallel with a 4.7-ohm resistor (index 4) to get ~0.825 ohms, then put a 4.3-ohm resistor (index 3) in parallel with a 2.7-ohm resistor (index 2) to get ~1.659 ohms, then connect those two sub-circuits in series to get ~2.483 ohms.

### Examples

**Example 1** — `baseResistances = [1, 5, 10]`, `resistance = 3.01`, `maxResistors = 3`

Answer: `((0)+(0))+(0)` — three 1-ohm resistors in series = 3 ohms (closest achievable value). You can reuse the same base value as many times as you want, up to `maxResistors` total components.

**Example 2** — `baseResistances = [1, 2]`, `resistance = pi * 10`, `maxResistors = 5`

Answer: `(1)+((1)//((1)+((0)//(1))))` — equivalent resistance ~31.4286, the closest to 10*pi achievable with at most 5 resistors from {1, 2}.

**Example 3** — `baseResistances = [1, 8]`, `resistance = 2.1`, `maxResistors = 4`

Answer: `(0)+(0)` — two 1-ohm resistors in series = 2 ohms. Although `((1)//(1))//((1)//(1))` also produces 2 ohms, it uses 4 resistors. Since 2 resistors achieves the same value, the 4-resistor version is not optimal (violates condition 2).

### Constraints

- Your solution's result must be within **+/- 0.0001%** of the expected equivalent resistance.
- When `resistance` is infinity (`float('inf')` in Python, `Double.MAX_VALUE` in Java), your goal is to maximize the equivalent resistance.
- You can use any base resistor value as many times as you want — the only limit is the total component count (`maxResistors`).
- Your code must be efficient enough to pass the 8 included test cases within the default timeout.

### Hint

Relative to their inputs, one combination function (series) is monotonically increasing and the other (parallel) is monotonically decreasing.

---

## Writing a Solution

You write one file — a `Solution` class that implements a single method. Everything else (test harness, utilities, interface definition) is provided.

### Python

Edit **`problems/equivalent-resistance/languages/python/solution.py`**:

```python
from solver import Solver
from resistor_utils import series, parallel, evaluate_config, base_scf, combine_scf


class Solution(Solver):

    def approximate(self, base_resistances, resistance, max_resistors):
        # Your code here — return an SCF string
        ...
```

### Java

Edit **`problems/equivalent-resistance/languages/java/src/main/java/com/stephenacomb/Solution.java`**:

```java
package com.stephenacomb;

import static com.stephenacomb.ResistorUtils.*;

public class Solution implements Solver {

    public String approximate(double[] baseResistances, double resistance, int maxResistors) {
        // Your code here — return an SCF string
        ...
    }
}
```

### Available utilities

Both languages provide these helper functions (already imported in the stub). Use them to build and evaluate SCF strings:

| Utility | Description | Example |
|---------|-------------|---------|
| `series(a, b)` | Returns `a + b` | `series(1.0, 2.0)` = `3.0` |
| `parallel(a, b)` | Returns `1/((1/a) + (1/b))` | `parallel(3.0, 6.0)` = `2.0` |
| `base_scf(index)` | Returns the SCF string for a single base resistor | `base_scf(0)` = `"0"` |
| `combine_scf(left, right, op)` | Combines two SCF strings with `"+"` or `"//"` | `combine_scf("0", "1", "+")` = `"(0)+(1)"` |
| `evaluate_config(scf, base_resistances)` | Evaluates an SCF string to its equivalent resistance | `evaluate_config("(0)+(1)", [1, 2])` = `3.0` |

Java uses camelCase: `evaluateConfig`, `baseScf`, `combineScf`.

You don't have to use these utilities — you can construct SCF strings however you like, as long as the result is a valid SCF string whose evaluated resistance matches the expected value.

### How tests verify your solution

Each test case calls your `approximate()` method, then evaluates the SCF string you return using `evaluate_config()` to compute the actual equivalent resistance. It then checks that the actual value is within 0.0001% of the expected optimal value. There are 8 test cases total.

---

## Running Tests

### Option A: Direct test runner

**Python** (requires Python 3.10+ and pytest):

```bash
cd problems/equivalent-resistance/languages/python
pip install -r requirements.txt
pytest -v
```

**Java** (requires JDK 11+ and Maven):

```bash
cd problems/equivalent-resistance/languages/java
mvn test
```

### Option B: Execution engine

The engine copies the harness to a temp directory, injects your solution file, runs the tests, and shows structured results. Run from the project root (requires Python 3.10+):

**Python:**

```bash
python3 -m engine run -p equivalent-resistance -l python -s problems/equivalent-resistance/languages/python/solution.py
```

**Java** (also requires JDK 11+ and Maven):

```bash
python3 -m engine run -p equivalent-resistance -l java -s problems/equivalent-resistance/languages/java/src/main/java/com/stephenacomb/Solution.java
```

Add `--json` for machine-readable JSON output.

The engine is useful if you want to test a solution file from anywhere without modifying the repo in-place.

### What to expect

Before you implement anything, all 8 tests will fail — that's expected. The stub returns `base_scf(0)` (just the first base resistor), which is almost never the optimal answer. A passing run looks like:

```
EQUIVALENT-RESISTANCE (python) -- 8/8 passed (0.05s)

  PASS test_1  (0.01s)
  PASS test_2  (0.003s)
  ...
```

---

## Prerequisites

### Python (3.10+)

Required for both Python solutions and the execution engine.

```bash
python3 --version
```

Most systems have Python pre-installed. If not, see https://www.python.org/downloads/.

### Java (JDK 11+)

Only required if solving in Java.

```bash
java --version
```

If not installed, any JDK distribution works (Temurin, Oracle, etc.). On Ubuntu/Debian:

```bash
sudo apt install openjdk-17-jdk
```

On macOS with Homebrew:

```bash
brew install openjdk@17
```

### Maven

Only required if solving in Java.

```bash
mvn --version
```

If not installed:

**Ubuntu/Debian:**

```bash
sudo apt install maven
```

**macOS with Homebrew:**

```bash
brew install maven
```

**Manual install (no sudo required):**

1. Download the latest binary archive from https://maven.apache.org/download.cgi (the `apache-maven-X.X.X-bin.tar.gz` link).
2. Extract it somewhere persistent, e.g.:
   ```bash
   tar -xzf apache-maven-*.tar.gz -C ~/tools
   ```
3. Add the `bin` directory to your `PATH`. In your `~/.bashrc` or `~/.zshrc`:
   ```bash
   export PATH="$HOME/tools/apache-maven-3.9.9/bin:$PATH"
   ```
4. Reload your shell (`source ~/.bashrc` or open a new terminal) and verify:
   ```bash
   mvn --version
   ```

---

## Project Structure

```
engine/                              # Execution engine (Python package)
  __init__.py                        # Exports run_solution()
  runner.py                          # Core engine logic
  junit_xml.py                       # JUnit XML parser
  __main__.py                        # CLI entry point (python -m engine ...)
problems/
  equivalent-resistance/
    problem.md                       # Full problem description
    testcases.json                   # Language-agnostic test case data
    languages/
      java/                          # Java Maven project
        pom.xml
        runner.json                  # Engine config (solution path, test command, XML glob)
        src/main/java/.../
          Solver.java                # Interface defining the contract
          ResistorUtils.java         # Utility library (series, parallel, SCF helpers)
          Solution.java              # Your solution goes here
        src/test/java/.../
          EquivalentResistanceTest.java  # 8 JUnit test cases
      python/
        runner.json                  # Engine config (solution path, test command, XML glob)
        solver.py                    # ABC defining the contract
        resistor_utils.py            # Utility library
        solution.py                  # Your solution goes here
        test_equivalent_resistance.py  # 8 pytest test cases
        requirements.txt
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the development plan: local web interface, sandboxed execution, and eventual deployment at apps.stephenacomb.com.
