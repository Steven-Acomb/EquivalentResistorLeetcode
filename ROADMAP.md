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

## Phase 2: Local Execution Engine

A CLI or script that can run a solution against a problem's test cases.

- [ ] Build a runner script (bash or python) that:
  - Takes a problem name, language, and solution file path
  - Copies the solution into the appropriate harness
  - Executes the language-specific test suite (mvn test / pytest)
  - Captures and parses results (pass/fail per test, execution time)
  - Returns a structured result (JSON)
- [ ] Docker-based sandboxing (optional for now, nice for consistency)
  - Dockerfiles per language with the needed runtimes
  - `docker-compose.yml` to make it one-command
- [ ] Measure and report wall-clock time per test case

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

- [ ] Time complexity scoring (compare against reference benchmarks per problem)
- [ ] Memory usage measurement and reporting
- [ ] Per-problem difficulty ratings
- [ ] Cleaner results UI (progress bars, color-coded pass/fail, expandable test details)
- [ ] Support for additional languages (JS/TS, C++, Go, etc. — each just needs a harness + Dockerfile)

## Future / Out of Scope for Now

- User accounts and auth
- Remote hosting and public access
- Leaderboards
- Problem submission by other users
