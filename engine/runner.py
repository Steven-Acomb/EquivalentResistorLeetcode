"""Core execution engine: copy harness, inject solution, run tests, return results."""

import glob
import json
import os
import shutil
import subprocess
import tempfile

from .junit_xml import parse_junit_xml


def run_solution(
    problem: str,
    language: str,
    solution_code: str,
    timeout: int = 120,
    problems_dir: str | None = None,
) -> dict:
    """Run a solution against a problem's test harness and return structured results.

    Args:
        problem: Problem slug (e.g. "equivalent-resistance")
        language: Language slug (e.g. "java", "python")
        solution_code: The solution source code to inject
        timeout: Max seconds for the test command
        problems_dir: Override path to problems/ directory

    Returns:
        Dict with status, tests, summary, stdout, stderr
    """
    if problems_dir is None:
        # Default: problems/ directory relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        problems_dir = os.path.join(project_root, "problems")

    harness_dir = os.path.join(problems_dir, problem, "languages", language)
    if not os.path.isdir(harness_dir):
        return _error_result(
            "build_error",
            f"Harness directory not found: {harness_dir}",
        )

    config_path = os.path.join(harness_dir, "runner.json")
    if not os.path.isfile(config_path):
        return _error_result(
            "build_error",
            f"runner.json not found in {harness_dir}",
        )

    with open(config_path) as f:
        config = json.load(f)

    solution_file = config["solution_file"]
    test_command = config["test_command"]
    junit_xml_glob = config["junit_xml_glob"]

    tmp_dir = None
    try:
        tmp_dir = tempfile.mkdtemp(prefix=f"engine_{problem}_{language}_")

        # Copy entire harness into temp dir
        work_dir = os.path.join(tmp_dir, "harness")
        shutil.copytree(harness_dir, work_dir)

        # Inject solution code
        solution_path = os.path.join(work_dir, solution_file)
        os.makedirs(os.path.dirname(solution_path), exist_ok=True)
        with open(solution_path, "w") as f:
            f.write(solution_code)

        # Run test command
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = result.stdout
            stderr = result.stderr
        except subprocess.TimeoutExpired as e:
            return {
                "status": "timeout",
                "tests": [],
                "summary": _empty_summary(),
                "stdout": (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""),
                "stderr": (e.stderr or b"").decode(errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or ""),
            }

        # Detect signal-based kills on Unix:
        # - Without shell: subprocess returns negative (-9 for SIGKILL)
        # - With shell: shell returns 128 + signal (137 for SIGKILL)
        if result.returncode < 0 or result.returncode > 128:
            return {
                "status": "runtime_error",
                "tests": [],
                "summary": _empty_summary(),
                "stdout": stdout,
                "stderr": stderr,
            }

        # Find and parse JUnit XML results
        xml_files = glob.glob(os.path.join(work_dir, junit_xml_glob))

        if not xml_files:
            # No XML produced — likely a build/compilation error
            return {
                "status": "build_error",
                "tests": [],
                "summary": _empty_summary(),
                "stdout": stdout,
                "stderr": stderr,
            }

        # Parse all XML files and merge results
        all_tests = []
        total_errors = 0
        for xml_file in sorted(xml_files):
            parsed = parse_junit_xml(xml_file)
            all_tests.extend(parsed["tests"])
            total_errors += parsed["summary"]["errors"]

        total = len(all_tests)
        passed = sum(1 for t in all_tests if t["passed"])
        failed = total - passed
        total_time = sum(t["time_seconds"] for t in all_tests)

        return {
            "status": "completed",
            "tests": all_tests,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": total_errors,
                "time_seconds": round(total_time, 3),
            },
            "stdout": stdout,
            "stderr": stderr,
        }

    finally:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)


def _empty_summary() -> dict:
    return {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "time_seconds": 0.0,
    }


def _error_result(status: str, message: str) -> dict:
    return {
        "status": status,
        "tests": [],
        "summary": _empty_summary(),
        "stdout": "",
        "stderr": message,
    }
