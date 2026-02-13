"""Core execution engine: copy harness, inject solution, run tests, return results."""

import glob
import json
import os
import resource
import shlex
import shutil
import signal
import subprocess
import tempfile
import threading
import time

from .junit_xml import parse_junit_xml

# Defaults if testcases.json has no "limits" section
_DEFAULT_TIME_SECONDS = 30
_DEFAULT_MEMORY_MB = 256


def run_solution(
    problem: str,
    language: str,
    solution_code: str,
    timeout: int = 120,
    problems_dir: str | None = None,
    per_test: bool = True,
) -> dict:
    """Run a solution against a problem's test harness and return structured results.

    Args:
        problem: Problem slug (e.g. "equivalent-resistance")
        language: Language slug (e.g. "java", "python")
        solution_code: The solution source code to inject
        timeout: Max seconds for the test command (batch mode) or setup command
        problems_dir: Override path to problems/ directory
        per_test: If True, run each test individually with resource limits

    Returns:
        Dict with status, tests, summary, stdout, stderr
    """
    if problems_dir is None:
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

    # Load testcases.json for test IDs and limits
    testcases_path = os.path.join(problems_dir, problem, "testcases.json")
    testcases = {}
    if os.path.isfile(testcases_path):
        with open(testcases_path) as f:
            testcases = json.load(f)

    limits = testcases.get("limits", {})
    time_limit = limits.get("time_seconds", _DEFAULT_TIME_SECONDS)
    memory_limit = limits.get("memory_mb", _DEFAULT_MEMORY_MB)

    solution_file = config["solution_file"]
    single_test_command = config.get("single_test_command")

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

        # Choose per-test or batch mode
        if per_test and single_test_command:
            test_ids = [t["id"] for t in testcases.get("tests", [])]
            return _run_per_test(
                config=config,
                work_dir=work_dir,
                test_ids=test_ids,
                time_limit=time_limit,
                memory_limit=memory_limit,
                timeout=timeout,
            )
        else:
            return _run_batch(
                config=config,
                work_dir=work_dir,
                timeout=timeout,
            )

    finally:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)


def _run_batch(config: dict, work_dir: str, timeout: int) -> dict:
    """Run all tests as a single subprocess (original behavior)."""
    test_command = config["test_command"]
    junit_xml_glob = config["junit_xml_glob"]

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

    # Detect signal-based kills on Unix
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
        return {
            "status": "build_error",
            "tests": [],
            "summary": _empty_summary(),
            "stdout": stdout,
            "stderr": stderr,
        }

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


def _run_per_test(
    config: dict,
    work_dir: str,
    test_ids: list,
    time_limit: int,
    memory_limit: int,
    timeout: int,
) -> dict:
    """Run each test individually with resource limits."""
    setup_command = config.get("setup_command")
    single_test_command = config["single_test_command"]
    junit_xml_glob = config["junit_xml_glob"]

    # Run setup command if present (e.g. compilation)
    if setup_command:
        try:
            setup_result = subprocess.run(
                setup_command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as e:
            return _error_result(
                "build_error",
                "Setup command timed out: " + setup_command,
            )

        if setup_result.returncode != 0:
            return {
                "status": "build_error",
                "tests": [],
                "summary": _empty_summary(),
                "stdout": setup_result.stdout,
                "stderr": setup_result.stderr,
            }

    # Run each test individually
    all_tests = []
    for test_id in test_ids:
        cmd_str = single_test_command.replace("{test_id}", str(test_id))
        cmd_args = shlex.split(cmd_str)

        test_result = _run_single_test(
            cmd_args=cmd_args,
            work_dir=work_dir,
            junit_xml_glob=junit_xml_glob,
            time_limit=time_limit,
            memory_limit=memory_limit,
            test_name=f"test_{test_id}",
        )
        all_tests.append(test_result)

    total = len(all_tests)
    passed = sum(1 for t in all_tests if t["verdict"] == "passed")
    failed = total - passed

    return {
        "status": "completed",
        "tests": all_tests,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": 0,
            "time_seconds": round(sum(t["time_seconds"] for t in all_tests), 3),
        },
        "stdout": "",
        "stderr": "",
    }


def _run_single_test(
    cmd_args: list,
    work_dir: str,
    junit_xml_glob: str,
    time_limit: int,
    memory_limit: int,
    test_name: str,
) -> dict:
    """Run a single test with RLIMIT_CPU and memory monitoring."""
    memory_limit_kb = memory_limit * 1024  # Convert MB to KB for /proc comparison

    def preexec_fn():
        # Set CPU time limit (soft = limit, hard = limit + 1 for grace)
        resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit + 1))

    # Remove any existing XML results before this test
    for old_xml in glob.glob(os.path.join(work_dir, junit_xml_glob)):
        os.remove(old_xml)

    wall_start = time.monotonic()

    try:
        proc = subprocess.Popen(
            cmd_args,
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=preexec_fn,
        )
    except OSError as e:
        return {
            "name": test_name,
            "verdict": "runtime_error",
            "time_seconds": 0.0,
            "memory_mb": 0.0,
            "message": f"Failed to start process: {e}",
        }

    # Start memory monitor
    monitor = _MemoryMonitor(proc.pid, memory_limit_kb)
    monitor.start()

    try:
        stdout_bytes, stderr_bytes = proc.communicate(timeout=time_limit + 5)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout_bytes, stderr_bytes = proc.communicate()

    wall_time = time.monotonic() - wall_start

    # Stop monitor and collect results
    monitor.stop()
    monitor.join(timeout=1)
    peak_mb = monitor.peak_mb
    killed_for_memory = monitor.killed

    # Determine verdict
    verdict = _determine_verdict(
        returncode=proc.returncode,
        killed_for_memory=killed_for_memory,
    )

    # Check XML for actual test result (covers both passed and failed verdicts)
    message = ""
    if verdict in ("passed", "failed"):
        xml_files = glob.glob(os.path.join(work_dir, junit_xml_glob))
        if xml_files:
            parsed = parse_junit_xml(sorted(xml_files)[0])
            if parsed["tests"]:
                xml_test = parsed["tests"][0]
                if not xml_test["passed"]:
                    verdict = "failed"
                    message = xml_test.get("message", "")
                else:
                    verdict = "passed"
        elif verdict == "passed":
            # No XML produced but process returned 0 — unusual
            verdict = "failed"
            message = "No test results produced"

    if verdict == "failed" and not message:
        stderr_text = stderr_bytes.decode(errors="replace") if stderr_bytes else ""
        if stderr_text:
            lines = stderr_text.strip().splitlines()
            message = lines[-1][:200] if lines else ""

    return {
        "name": test_name,
        "verdict": verdict,
        "time_seconds": round(wall_time, 3),
        "memory_mb": round(peak_mb, 1),
        "message": message if message else None,
    }


def _determine_verdict(returncode: int, killed_for_memory: bool) -> str:
    """Map process exit status to a verdict string."""
    if killed_for_memory:
        return "memory_limit_exceeded"

    if returncode == -signal.SIGXCPU:
        return "time_limit_exceeded"

    if returncode == -signal.SIGKILL:
        # SIGKILL without memory kill — likely RLIMIT_CPU hard limit
        return "time_limit_exceeded"

    if returncode == 0:
        return "passed"

    if returncode > 0:
        return "failed"

    # Any other negative returncode (other signals)
    return "runtime_error"


class _MemoryMonitor(threading.Thread):
    """Polls /proc/{pid}/status for VmHWM and kills if over limit."""

    def __init__(self, pid: int, limit_kb: int):
        super().__init__(daemon=True)
        self.pid = pid
        self.limit_kb = limit_kb
        self.peak_mb = 0.0
        self.killed = False
        self._stop_event = threading.Event()

    def run(self):
        status_path = f"/proc/{self.pid}/status"
        while not self._stop_event.is_set():
            try:
                with open(status_path) as f:
                    for line in f:
                        if line.startswith("VmHWM:"):
                            hwm_kb = int(line.split()[1])
                            hwm_mb = hwm_kb / 1024.0
                            if hwm_mb > self.peak_mb:
                                self.peak_mb = hwm_mb
                            if hwm_kb > self.limit_kb:
                                self.killed = True
                                try:
                                    os.kill(self.pid, signal.SIGKILL)
                                except ProcessLookupError:
                                    pass
                                return
                            break
            except (FileNotFoundError, ProcessLookupError):
                # Process already exited
                return
            except (PermissionError, OSError):
                return
            self._stop_event.wait(0.1)

    def stop(self):
        self._stop_event.set()


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
