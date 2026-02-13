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
- [x] ~~Reorder tests~~ — no longer needed: per-test execution isolates each test in its own subprocess, so a TLE/MLE on test 1 doesn't block the rest
- [x] Add brute-force examples per language under `problems/.../examples/` with instructions in README for running them via the engine's `-s` flag
- [x] Clarify engine workflow in README: document per-test output format, verdicts (TLE/MLE/RTE), `--no-per-test` flag, and brute-force examples

## Phase 3: Local Problem Workbench

A locally-hosted, browser-based interface for reading the problem, writing solutions, and
running tests — the core LeetCode workflow, for a single problem, running entirely on the
user's machine after a git clone.

This is a prototype/intermediate step. It does not need to be production-ready or
forward-compatible with the eventual hosted version at apps.stephenacomb.com, but the
API contract between frontend and backend should be designed as if it could be reused.

### Requirements

#### R1. Setup & Environment

- **R1.1**: Starting the workbench requires one command from the repo root (e.g.
  `python3 -m server` or `make run`).
- **R1.2**: The only required dependency is Python 3.10+ (already required for the engine).
  No Node.js, no frontend build step, no additional system packages.
- **R1.3**: Language-specific toolchains (JDK + Maven for Java) are only required if the
  user selects that language. Selecting a language whose toolchain is missing produces a
  clear error, not a crash.
- **R1.4**: The server runs on `localhost` with a configurable port (default `8000` or
  similar). Opening the URL in any modern browser lands you on the workbench.

#### R2. Problem Display

- **R2.1**: The problem description is rendered from the existing `problem.md`, converted to
  formatted HTML. No duplicated or hard-coded problem content in the frontend.
- **R2.2**: The rendered description includes all sections a solver needs: problem statement,
  SCF format explanation, examples, constraints, and available utilities.
- **R2.3**: The description is always visible alongside the editor (split-pane, tab, or
  scrollable panel — layout TBD). The user should not have to navigate away from the editor
  to re-read the problem.

#### R3. Language Selection

- **R3.1**: The workbench presents all available languages, auto-discovered from the
  filesystem (`problems/<problem>/languages/*/runner.json`). Adding a new language directory
  with valid harness files makes it appear as an option with no server or frontend changes.
- **R3.2**: Selecting a language loads that language's solution stub into the editor and sets
  the appropriate syntax highlighting mode.
- **R3.3**: Switching languages preserves each language's editor state independently. The
  user can switch between languages without losing work in either.

#### R4. Code Editor

- **R4.1**: The editor uses Monaco (VS Code's editor component) or an equivalent that
  provides syntax highlighting, bracket matching, and standard keyboard shortcuts
  (undo/redo, find/replace, etc.).
- **R4.2**: The editor is pre-filled with the solution stub for the selected language on
  first load. If a saved solution exists on disk, that is loaded instead.
- **R4.3**: The editor content is the complete source file the solver would write (e.g. the
  full `Solution.java` or `solution.py`). No hidden boilerplate or template injection —
  what the user sees is what gets sent to the engine.

#### R5. Test Execution & Results

- **R5.1**: A "Run" button sends the editor's current code to the backend and displays
  per-test results.
- **R5.2**: Results show each test with its verdict (`PASS`, `FAIL`, `TLE`, `MLE`, `RTE`),
  wall time, and peak memory.
- **R5.3**: Failed tests show the failure message (assertion detail or error output). This
  is expandable/collapsible so it doesn't overwhelm the results list.
- **R5.4**: A summary line shows total passed/failed and aggregate time.
- **R5.5**: While tests are running, the UI shows a loading/progress state. The UI remains
  responsive (the run is async). The user can continue reading the problem or editing code
  while waiting.
- **R5.6**: Build errors (compilation failures, syntax errors) display the relevant error
  output clearly, distinguishable from test failures.
- **R5.7**: Only one run can be in flight at a time. The Run button is disabled while a
  previous run is executing.

#### R6. Solution Persistence

- **R6.1**: Solutions are saved to a `solutions/` directory in the repo root, organized by
  problem and language (e.g. `solutions/equivalent-resistance/python/solution.py`). This
  directory is gitignored by default but users can commit solutions on their own branches.
- **R6.2**: Saving is explicit — a "Save" button (or Ctrl+S) writes the current editor
  content to the solutions directory.
- **R6.3**: On load, if a saved solution exists in `solutions/`, it is loaded into the
  editor. Otherwise the language's stub is loaded.
- **R6.4**: A "Reset" action restores the editor to the original solution stub for the
  current language, with a confirmation prompt. This also deletes the saved file.
- **R6.5**: The workbench never modifies harness files (`solution.py`/`Solution.java` in
  the problems directory). All user work goes to `solutions/`.

#### R7. API Contract

- **R7.1**: The backend exposes a small JSON API. At minimum:
  - `GET /api/problem` — returns problem metadata, rendered description (HTML), and list of
    available languages with their stubs.
  - `POST /api/run` — accepts `{language, code}`, returns the engine's structured result
    (status, per-test verdicts, summary, stdout/stderr).
  - `GET /api/solution/{language}` — returns the saved solution if one exists, otherwise
    the stub.
  - `PUT /api/solution/{language}` — saves solution code to the solutions directory.
  - `DELETE /api/solution/{language}` — deletes saved solution (reset to stub).
- **R7.2**: The API is stateless. Each request is self-contained. No sessions, no auth.
- **R7.3**: The API contract is documented (even if just in code comments or a short spec)
  so it can inform the future production API.

#### R8. Extensibility

- **R8.1**: Adding a new language requires only adding harness files under
  `problems/<problem>/languages/<lang>/` (runner.json, stub, tests, utilities). No server
  or frontend code changes.
- **R8.2**: Adding or modifying test cases requires only editing `testcases.json`. No server
  or frontend code changes.
- **R8.3**: If the problem description (`problem.md`) is updated, the change is reflected on
  next page load without restarting the server.

#### R9. Out of Scope

These are explicitly not requirements for Phase 3:

- Multiple problems or a problem browser
- User accounts, authentication, or multi-user support
- Solution history or versioning (beyond the single saved file per language)
- Deployment to a remote host
- Docker or containerized execution
- Hidden test cases or a "Submit" vs "Run" distinction
- Mobile or responsive layout (desktop browser is fine)
- Offline support (localhost is always available)

### Architecture

- **Backend**: FastAPI + Uvicorn. Single Python process serves both the JSON API and static
  frontend files. Async-capable, so long-running test executions don't block the server.
  FastAPI's auto-generated OpenAPI docs satisfy R7.3.
- **Frontend**: Static HTML/CSS/JS — no build step, no Node.js. One `index.html`, one
  `app.js`, one `style.css`, served from `server/static/`. All interactivity via vanilla JS
  and `fetch()` calls to the API.
- **Editor**: Monaco Editor loaded from CDN (jsDelivr). Provides syntax highlighting,
  bracket matching, and standard keyboard shortcuts.
- **CSS**: Pico CSS (classless, from CDN) for typography, buttons, forms, and tables.
  Custom CSS only for app-specific layout (split panes, results panel, verdict colors).
- **Markdown rendering**: Server-side via Python `markdown` library. The API returns
  pre-rendered HTML; the frontend just inserts it.
- **Package structure**: `server/` directory alongside `engine/`, with `__main__.py` for
  `python3 -m server` entry point.

### Tasks

#### T1. Server scaffold & static file serving (done)
- [x] Create `server/` package: `__init__.py`, `__main__.py`, `app.py`
- [x] FastAPI app with configurable port, static file serving from `server/static/`
- [x] `server/requirements.txt` with fastapi, uvicorn, markdown
- [x] Placeholder `index.html` that loads Pico CSS and Monaco from CDN
- [x] Verify `python3 -m server` starts and serves the placeholder page
- [x] `environment.yml` conda environment with all dependencies
- Satisfies: R1.1, R1.2, R1.4

#### T2. API endpoints (done)
- [x] `GET /api/problem` — read `problem.md`, render to HTML via `markdown` library,
  discover languages from filesystem, return stubs and metadata
- [x] `POST /api/run` — accept `{language, code}`, call `engine.run_solution()` in thread
  pool, return structured result. Return clear error if language toolchain missing (R1.3).
- [x] `GET /api/solution/{language}` — return saved solution from `solutions/` if exists,
  otherwise return the language's stub
- [x] `PUT /api/solution/{language}` — write solution to
  `solutions/<problem>/<language>/<solution_file>`
- [x] `DELETE /api/solution/{language}` — delete saved solution file
- [x] Add `solutions/` to `.gitignore`
- Satisfies: R1.3, R6.1, R6.5, R7.1, R7.2, R7.3, R8.1, R8.2, R8.3

#### T3. Frontend: page layout & problem display (done)
- [x] Split-pane layout — problem description on the left, editor + results on the right
- [x] Fetch `GET /api/problem` on load, render description HTML into left panel
- [x] Custom CSS for split-pane, scrollable panels, overall page structure
- Satisfies: R2.1, R2.2, R2.3

#### T4. Frontend: Monaco editor & language switching (done)
- [x] Initialize Monaco editor in the right panel
- [x] Language selector dropdown populated from `/api/problem` response
- [x] Selecting a language fetches `GET /api/solution/{language}` and loads into editor
- [x] Set Monaco language mode based on selection (python, java)
- [x] Preserve per-language editor state in memory when switching (unsaved edits kept)
- Satisfies: R3.1, R3.2, R3.3, R4.1, R4.2, R4.3

#### T5. Frontend: test execution & results (done)
- [x] Run button sends `POST /api/run` with current language and editor content
- [x] Loading/spinner state while request is in flight; Run button disabled (R5.7)
- [x] Results panel below editor showing per-test verdict, time, memory (R5.2)
- [x] Summary line: passed/failed count and total time (R5.4)
- [x] Expandable/collapsible failure messages (R5.3)
- [x] Build error display distinguishable from test failures (R5.6)
- [x] Color-coded verdict labels: green PASS, red FAIL, orange TLE, purple MLE, gray RTE
- Satisfies: R5.1–R5.7

#### T6. Frontend: solution persistence (done)
- [x] Save button and Ctrl+S shortcut → `PUT /api/solution/{language}` (R6.2)
- [x] On load, `GET /api/solution/{language}` returns saved solution or stub (R6.3)
- [x] Reset button with confirmation prompt → `DELETE /api/solution/{language}`, reload
  stub into editor (R6.4)
- Satisfies: R6.1–R6.4

#### T7. End-to-end verification
- [ ] Start server, open browser, complete full workflow in Python (load, edit, run, save,
  reset)
- [ ] Repeat in Java (verify setup_command runs, results display correctly)
- [ ] Verify language auto-discovery (languages appear without code changes)
- [ ] Verify problem.md changes reflected on reload (R8.3)
- [ ] Verify missing toolchain produces clear error (R1.3)
- Satisfies: all requirements verified end-to-end

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
