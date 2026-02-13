# Equivalent Resistor Leetcode

A custom leetcode-style coding challenge platform, starting with an electrical engineering optimization problem.

## The Challenge

When designing circuits, engineers often can't find a single resistor with the exact value they need. Instead, they combine resistors in **series** (resistances add: `Ra + Rb`) and **parallel** (resistances combine: `1/((1/Ra) + (1/Rb))`) to approximate a target value. With a handful of standard resistor values and enough components, you can get surprisingly close to any target — but finding the *best* combination is computationally hard.

**Your task:** Given an array of available resistor values, a maximum number of components, and a target resistance, find the series/parallel configuration that best approximates the target. Return your answer as a string in **Serializable Configuration Format** (SCF), a nested parenthesized notation that encodes both the structure and the components used.

See [`problems/equivalent-resistance/problem.md`](problems/equivalent-resistance/problem.md) for the full problem statement, SCF format spec, examples, and constraints.

## How It Works

Each problem in this repo has:
- A **problem description** (`problem.md`) with the full specification
- **Test cases** (`testcases.json`) defining inputs and expected outputs
- Per-language **harness code** that runs your solution against the tests and reports results
- A **solution stub** — the one file you edit to write your solution

For the Equivalent Resistance problem, the harness provides a `Solver` interface and a `ResistorUtils` utility class with helper functions (series/parallel math, SCF string builders, and an SCF evaluator). You write a `Solution` class that implements the interface.

## Trying It

### Java

1. Clone the repo
2. Open `problems/equivalent-resistance/languages/java/src/main/java/com/stephenacomb/Solution.java` — this is the only file you edit
3. Implement the `approximate()` method
4. Run the tests:

```bash
cd problems/equivalent-resistance/languages/java
mvn test
```

### Python

1. Clone the repo
2. Open `problems/equivalent-resistance/languages/python/solution.py` — this is the only file you edit
3. Implement the `approximate()` method
4. Run the tests:

```bash
cd problems/equivalent-resistance/languages/python
pip install -r requirements.txt
pytest -v
```

Each test suite runs 8 test cases and reports a score. All tests will fail until you implement a solution — that's expected.

### What's available to your solution

Both languages provide the same utilities (already imported in the stub):

| Utility | Description |
|---------|-------------|
| `series(a, b)` | Returns `a + b` |
| `parallel(a, b)` | Returns `1/((1/a) + (1/b))` |
| `evaluate_config(scf, base_resistances)` | Evaluates an SCF string to a resistance value |
| `base_scf(index)` | Returns the SCF string for a base resistor at the given index |
| `combine_scf(left, right, op)` | Combines two SCF strings with `"+"` or `"//"` |

Java uses camelCase (`evaluateConfig`, `baseScf`, `combineScf`). Python uses snake_case.

## Project Structure

```
problems/
  equivalent-resistance/
    problem.md                       # Full problem description
    testcases.json                   # Language-agnostic test case data
    languages/
      java/                          # Java Maven project
        pom.xml
        src/main/java/.../
          Solver.java                # Interface defining the contract
          ResistorUtils.java         # Utility library (series, parallel, SCF helpers)
          Solution.java              # Your solution goes here
        src/test/java/.../
          EquivalentResistanceTest.java  # 8 JUnit test cases
      python/
        solver.py                    # ABC defining the contract
        resistor_utils.py            # Utility library
        solution.py                  # Your solution goes here
        test_equivalent_resistance.py  # 8 pytest test cases
        requirements.txt
```

## Prerequisites

### Python (3.10+)

Check if you have it:

```bash
python3 --version
```

Most systems have Python pre-installed. If not, see https://www.python.org/downloads/.

### Java (JDK 11+)

Check if you have it:

```bash
java --version
```

If not, install a JDK. Any distribution works (Temurin, Oracle, etc.). On Ubuntu/Debian:

```bash
sudo apt install openjdk-17-jdk
```

On macOS with Homebrew:

```bash
brew install openjdk@17
```

### Maven

Check if you have it:

```bash
mvn --version
```

If not:

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

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the development plan: Python support, local web interface, sandboxed execution, and eventual deployment at apps.stephenacomb.com.
