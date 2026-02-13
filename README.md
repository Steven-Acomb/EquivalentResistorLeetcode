# Equivalent Resistor Leetcode

A custom leetcode-style coding challenge platform, starting with an electrical engineering optimization problem: given a set of available resistor values, find the best series/parallel configuration that approximates a target resistance.

## Project Structure

```
problems/                        # Problem definitions
  equivalent-resistance/
    problem.md                   # Full problem description
    testcases.json               # Language-agnostic test case data
    languages/
      java/                      # Java Maven project (harness + solution stub)
        pom.xml
        src/
          main/java/.../
            Resistor.java              # Series/parallel functions
            ResistorApproximator.java  # Solution stub + SCF evaluator
          test/java/.../
            ResistorApproximatorTest.java  # JUnit test suite
```

## Running (Java)

```bash
cd problems/equivalent-resistance/languages/java
mvn test
```

Implement the `approximate()` method in `ResistorApproximator.java` and run the tests to check your solution. See `problems/equivalent-resistance/problem.md` for the full problem statement.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the development plan: Python support, local web interface, sandboxed execution, and eventual deployment at apps.stephenacomb.com.
