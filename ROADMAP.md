# Roadmap

Local-first leetcode-like platform, all runnable from a single repo clone.

## Phase 0: Repo Restructure (done)

Reorganize from single-Java-problem layout to a multi-language platform structure.

- [x] Define a standard problem format (metadata, description, per-language stubs, test cases)
- [x] Extract the Equivalent Resistance problem into that format
  - Separate problem description (markdown) from code
  - Separate test cases (inputs/expected outputs) from language-specific test harnesses
  - Move Java solution stub and harness into a `languages/java/` subtree
- [x] Define a standard solution format — Option C (interface/contract implementation)
  - Solver writes a complete file implementing a language-specific interface (e.g. `Solver`)
  - Harness provides the interface, utilities (`ResistorUtils`), and tests
  - Solver's file is self-contained and the only file they edit (`Solution.java`)
  - Utility layer provides series/parallel functions, SCF evaluator, SCF builder helpers
- [x] Create a top-level project structure:
  ```
  problems/
    equivalent-resistance/
      problem.md
      testcases.json
      languages/
        java/                 # Maven project
          src/main/java/.../
            Solver.java       # Interface (contract)
            ResistorUtils.java # Utilities for solvers
            Solution.java     # Solver's stub (only file they edit)
          src/test/java/.../
            EquivalentResistanceTest.java
  ```

## Phase 1: Python Support (done)

Add Python as a second supported language for the Equivalent Resistance problem.

- [x] Port `ResistorUtils` to Python (`resistor_utils.py`: series, parallel, evaluate_config, base_scf, combine_scf)
- [x] Create Python `Solver` base class (`solver.py`: ABC with abstract `approximate` method)
- [x] Write Python test harness (`test_equivalent_resistance.py`: 8 pytest test cases matching Java)
- [x] Create Python `Solution` stub (`solution.py`: implements Solver, returns `base_scf(0)`)
- [x] Verify `evaluate_config` produces identical values across Java and Python for all reference configs

## Phase 2: Local Execution Engine (done)

A Python library + CLI that takes solution source code, a problem, and a language, runs the
solution against the test harness in an isolated workspace, and returns structured results.

### Requirements

- **Source code in, structured results out**: the engine takes solution text (not a file path),
  a problem ID, and a language ID. Returns JSON-serializable results. The caller handles
  I/O (reading files, HTTP bodies, DB records).
- **Language-agnostic orchestration**: per-language config declares where the solution file goes,
  what test command to run, and where to find JUnit XML output. Adding a language means adding
  config, not modifying the engine.
- **Isolation**: copy the harness to a temp directory, inject the solution, run, discard.
  Never modify repo files in-place. Supports concurrent runs.
- **Timeout**: configurable wall-clock timeout per run, reported as a distinct result.
- **Stateless and idempotent**: no state between runs, same inputs always produce same outputs.
- **Dual entry point**: callable as a Python function (for the web backend) and as a CLI
  (for developers). Same core logic.
- **JUnit XML for result parsing**: Maven/surefire produces it automatically, pytest via
  `--junitxml` flag. Engine has one XML parser. Score computed engine-side (count passing tests).

### Tasks

- [x] Define per-language config format (solution file path, test command, JUnit XML location)
- [x] Create language configs for Java and Python
- [x] Build the core engine (Python library):
  - Copy harness to temp dir
  - Inject solution file
  - Run test command with timeout
  - Parse JUnit XML output into structured results
  - Clean up temp dir
- [x] Build CLI wrapper (reads a solution file, calls the engine, pretty-prints results)
- [ ] Docker-based sandboxing (optional for now, nice for consistency)
  - Dockerfiles per language with the needed runtimes
  - `docker-compose.yml` to make it one-command

## Phase 2.5: Test & Engine Hardening

Findings from acid-testing the platform with brute-force solutions in both languages.

- [x] Fix engine error reporting: detect signal-based kills (SIGKILL/OOM) and report as "RUNTIME ERROR (process killed)" instead of "BUILD ERROR"
- [x] Per-test execution with resource limits: engine runs each test individually with `RLIMIT_CPU` time limits and `/proc`-based memory monitoring. Produces distinct verdicts: `passed`, `failed`, `time_limit_exceeded` (`TLE`), `memory_limit_exceeded` (`MLE`), `runtime_error` (`RTE`). Limits defined in `testcases.json` (language-agnostic), enforced by the engine. `--no-per-test` flag falls back to batch mode. Supersedes earlier language-specific timeout approach (pytest-timeout / Surefire timeout).
- [ ] Reorder tests: move the E96 151-value test (test 1) to the end of the suite so simpler tests run first
- [x] Add brute-force examples per language under `problems/.../examples/` with instructions in README for running them via the engine's `-s` flag
- [x] Clarify engine workflow in README: document per-test output format, verdicts (TLE/MLE/RTE), `--no-per-test` flag, and brute-force examples

## Phase 3: Local Web Interface

A locally-hosted webapp for browsing problems, editing code, and submitting solutions.

- [ ] Choose frontend stack (e.g. React + Vite, or something lighter like plain HTML + HTMX)
- [ ] Choose backend stack (e.g. FastAPI or Flask, since Python is already in the picture)
- [ ] Problem browser page
  - List available problems
  - Render problem description from markdown
- [ ] Solution editor page
  - Embed Monaco editor (VS Code's editor component) with syntax highlighting
  - Language selector dropdown
  - Load solution stub as default content
  - Save/load solutions to `solutions/` directory
- [ ] Submission and results
  - Submit button calls the backend, which invokes the execution engine from Phase 2
  - Display per-test pass/fail, execution time
  - Show stdout/stderr output for debugging
- [ ] Single `docker compose up` or `make run` to start everything

## Phase 4: Solution & Test Case Management

Niceties for authoring problems and working with solutions.

- [ ] Auto-save solutions on edit (to `solutions/` dir)
- [ ] Solution history (git-backed or simple file versioning)
- [ ] Test case editor in the web UI
  - View existing test cases
  - Add/edit/delete test cases
  - Validate test cases by running reference solutions against them
- [ ] Support for hidden vs. visible test cases (visible ones shown in the problem description)
- [ ] Import/export of problems as self-contained archives

## Phase 5: Scoring & Polish

- [ ] Time complexity scoring (compare against reference benchmarks per problem; per-test wall time and peak memory already reported by the engine)
- [ ] Memory usage measurement and reporting (basic peak-RSS tracking done; JVM memory tracking limited to Maven parent process until Docker sandboxing)
- [ ] Per-problem difficulty ratings
- [ ] Cleaner results UI (progress bars, color-coded pass/fail, expandable test details)
- [ ] Support for additional languages (JS/TS, C++, Go, etc. — each just needs a harness + Dockerfile)

## Future / Out of Scope for Now

- User accounts and auth
- Remote hosting and public access
- Leaderboards
- Problem submission by other users
