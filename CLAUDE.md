# CLAUDE.md

## What This Project Is

A custom leetcode-style coding challenge platform. The first (and currently only) problem is "Equivalent Resistance" — an optimization problem from electrical engineering where solvers must find the best series/parallel resistor configuration to approximate a target resistance value.

The platform is being built incrementally: local-first development now, eventually deployed as a webapp at apps.stephenacomb.com.

## Current State

Phase 0 (repo restructure) is complete. The repo contains:

- **One problem** (Equivalent Resistance) with a full description, test cases, and a Java harness.
- **Java only** — the solution stub is `ResistorApproximator.approximate()`, the test suite is JUnit 4, built with Maven.
- **No web interface yet** — solutions are tested by running `mvn test` directly.
- **The `approximate()` method is intentionally unimplemented** — it's the challenge. Don't implement it unless asked.

## Repo Structure

```
problems/                           # Problem definitions (pure data, no app logic)
  equivalent-resistance/
    problem.md                      # Problem description (markdown)
    testcases.json                  # Language-agnostic test inputs/expected outputs
    languages/
      java/                         # Full Maven project
        pom.xml
        src/main/java/.../
          Resistor.java             # Series (+) and parallel (//) functions
          ResistorApproximator.java # SCF evaluator + solution stub
        src/test/java/.../
          ResistorApproximatorTest.java  # 8 JUnit test cases
```

Future directories (not yet created):
- `frontend/` — Web UI (SPA with Monaco editor)
- `server/` — API server (serves problems, dispatches execution)
- `runners/` — Dockerfiles for sandboxed per-language execution
- `solutions/` — Gitignored directory for local user work

## How It Fits Into stephenacomb.com

The main site (stephenacomb.com) is a static Astro portfolio deployed via Cloudflare Pages or Netlify. Interactive projects like this one live separately under apps.stephenacomb.com as independently deployable webapps.

This means this project must be:
- **Self-contained** — standalone frontend + backend, no shared runtime with the main site
- **Environment-driven** — base URL, API origin, and asset paths come from config, not hardcoded paths
- **Deployment-agnostic** — must work locally (docker compose up), at a preview URL, and at apps.stephenacomb.com without code changes
- **Loosely coupled** — auth, persistence, and storage are pluggable; starts stateless, can integrate shared infra later

## Development Plan (see ROADMAP.md for details)

0. ~~Repo restructure~~ (done)
1. Python support — port harness/stub for Equivalent Resistance
2. Local execution engine — runner script that takes problem + language + solution, returns results
3. Local web interface — Monaco editor, problem viewer, submit/results via HTTP API
4. Solution & test case management — auto-save, history, test case editor
5. Scoring & polish — time/memory measurement, difficulty ratings, more languages

## Key Technical Decisions

- **Problem format**: Each problem has a markdown description, a `testcases.json` with language-agnostic data, and per-language directories containing a harness (support code + test runner) and a stub (starter code for the solver).
- **testcases.json**: Some test targets are computed by evaluating a reference SCF config string (indicated by `{"type": "evaluateConfig", "config": "..."}`), others are literal numbers. `"MAX"` represents the language's max float value.
- **SCF (Serializable Configuration Format)**: A nested parenthesized string format for resistor configurations. `(0)` = base resistor at index 0, `(A)+(B)` = series, `(A)//(B)` = parallel. The evaluator is already implemented in Java.
- **Optimal approximation**: Closest equivalent resistance to target (condition 1), using fewest components (condition 2 tiebreaker).

## Conventions

- Keep the problem content (descriptions, test cases) language-agnostic. Language-specific code lives under `languages/<lang>/`.
- The solver edits files in `stub/` (or in the current Java layout, the `approximate()` method). Everything else is harness.
- Build artifacts (`target/`, `__pycache__/`, etc.) should be gitignored.
- Don't implement the `approximate()` method — that's the challenge for humans to solve.
