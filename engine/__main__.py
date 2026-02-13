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
            if test["passed"]:
                print(f"  PASS {name}  ({t}s)")
            else:
                msg = test.get("message", "")
                # Truncate long messages
                if len(msg) > 120:
                    msg = msg[:117] + "..."
                print(f"  FAIL {name}  ({t}s)  {msg}")

    print()


if __name__ == "__main__":
    main()
