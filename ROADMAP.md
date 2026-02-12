# Roadmap

Local-first leetcode-like platform, all runnable from a single repo clone.

## Phase 0: Repo Restructure

Reorganize from single-Java-problem layout to a multi-language platform structure.

- [ ] Define a standard problem format (metadata, description, per-language stubs, test cases)
- [ ] Extract the Equivalent Resistance problem into that format
  - Separate problem description (markdown) from code
  - Separate test cases (inputs/expected outputs) from language-specific test harnesses
  - Move Java solution stub and harness into a `languages/java/` subtree
- [ ] Define a standard solution format (where user solutions live, how they're named)
- [ ] Create a top-level project structure, e.g.:
  ```
  problems/
    equivalent-resistance/
      description.md
      testcases.json          # language-agnostic inputs/expected outputs
      languages/
        java/
          stub/               # starter code given to solver
          harness/            # test runner, support code (Resistor.java, etc.)
        python/
          stub/
          harness/
  solutions/                  # gitignored by default, user work lives here
    equivalent-resistance/
      java/
      python/
  ```

## Phase 1: Python Support

Add Python as a second supported language for the Equivalent Resistance problem.

- [ ] Port `Resistor.java` functionality to Python (series/parallel functions)
- [ ] Port `evaluateResistorConfiguration` to Python (SCF parser)
- [ ] Write Python test harness equivalent to `ResistorApproximatorTest.java`
- [ ] Create Python solution stub (`approximate` function, returns `"(0)"`)
- [ ] Verify the test cases produce the same expected values across both languages

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
- AI-assisted hint system
