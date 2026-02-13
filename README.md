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

## Prerequisites

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

## Running (Java)

```bash
cd problems/equivalent-resistance/languages/java
mvn test
```

Implement the `approximate()` method in `ResistorApproximator.java` and run the tests to check your solution. See `problems/equivalent-resistance/problem.md` for the full problem statement.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the development plan: Python support, local web interface, sandboxed execution, and eventual deployment at apps.stephenacomb.com.
