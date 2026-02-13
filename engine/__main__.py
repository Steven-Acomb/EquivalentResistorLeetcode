"""CLI entry point: python -m engine run -p <problem> -l <language> -s <solution_file>"""

import argparse
import json
import sys

from .runner import run_solution


def main():
    parser = argparse.ArgumentParser(
        prog="engine",
        description="Run a solution against a problem's test harness",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a solution")
    run_parser.add_argument("-p", "--problem", required=True, help="Problem slug")
    run_parser.add_argument("-l", "--language", required=True, help="Language slug")
    run_parser.add_argument("-s", "--solution", required=True, help="Path to solution file")
    run_parser.add_argument("--json", action="store_true", dest="json_output", help="Output raw JSON")
    run_parser.add_argument("--timeout", type=int, default=120, help="Timeout in seconds")
    run_parser.add_argument(
        "--no-per-test", action="store_true", dest="no_per_test",
        help="Run all tests in a single batch instead of individually",
    )

    args = parser.parse_args()

    if args.command != "run":
        parser.print_help()
        sys.exit(1)

    try:
        with open(args.solution) as f:
            solution_code = f.read()
    except FileNotFoundError:
        print(f"Error: Solution file not found: {args.solution}", file=sys.stderr)
        sys.exit(1)

    result = run_solution(
        problem=args.problem,
        language=args.language,
        solution_code=solution_code,
        timeout=args.timeout,
        per_test=not args.no_per_test,
    )

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        _pretty_print(result, args.problem, args.language)

    # Exit with non-zero if any tests failed or errored
    if result["status"] != "completed" or result["summary"]["passed"] != result["summary"]["total"]:
        sys.exit(1)


def _pretty_print(result: dict, problem: str, language: str):
    summary = result["summary"]
    status = result["status"]

    header = f"{problem.upper()} ({language})"

    if status == "timeout":
        print(f"\n{header} -- TIMEOUT\n")
        print("  The test command exceeded the time limit.")
    elif status == "runtime_error":
        print(f"\n{header} -- RUNTIME ERROR (process killed)\n")
        if result["stderr"]:
            for line in result["stderr"].strip().splitlines()[-20:]:
                print(f"  {line}")
    elif status == "build_error":
        print(f"\n{header} -- BUILD ERROR\n")
        if result["stderr"]:
            for line in result["stderr"].strip().splitlines()[-20:]:
                print(f"  {line}")
    else:
        passed = summary["passed"]
        total = summary["total"]
        time_s = summary["time_seconds"]
        print(f"\n{header} -- {passed}/{total} passed ({time_s}s)\n")

        for test in result["tests"]:
            name = test["name"]
            t = test["time_seconds"]

            # Per-test mode (has "verdict" field)
            if "verdict" in test:
                verdict = test["verdict"]
                mem = test.get("memory_mb", 0)
                msg = test.get("message") or ""

                _VERDICT_LABELS = {
                    "passed": "PASS",
                    "failed": "FAIL",
                    "time_limit_exceeded": "TLE ",
                    "memory_limit_exceeded": "MLE ",
                    "runtime_error": "RTE ",
                }
                label = _VERDICT_LABELS.get(verdict, verdict.upper())

                if verdict == "passed":
                    print(f"  {label} {name}  ({t}s, {mem}MB)")
                else:
                    if len(msg) > 120:
                        msg = msg[:117] + "..."
                    suffix = f"  {msg}" if msg else ""
                    print(f"  {label} {name}  ({t}s, {mem}MB){suffix}")

            # Batch mode (has "passed" field)
            else:
                if test["passed"]:
                    print(f"  PASS {name}  ({t}s)")
                else:
                    msg = test.get("message", "")
                    if len(msg) > 120:
                        msg = msg[:117] + "..."
                    print(f"  FAIL {name}  ({t}s)  {msg}")

    print()


if __name__ == "__main__":
    main()
