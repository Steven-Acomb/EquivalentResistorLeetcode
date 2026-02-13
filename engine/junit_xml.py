"""JUnit XML parser using stdlib xml.etree.ElementTree."""

import xml.etree.ElementTree as ET


def parse_junit_xml(xml_path: str) -> dict:
    """Parse a JUnit XML file into structured results.

    Returns a dict with:
        tests: list of {name, passed, time_seconds, message}
        summary: {total, passed, failed, errors, time_seconds}
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Handle both <testsuites><testsuite>... and bare <testsuite>...
    if root.tag == "testsuites":
        suites = root.findall("testsuite")
    elif root.tag == "testsuite":
        suites = [root]
    else:
        return {"tests": [], "summary": _empty_summary()}

    tests = []
    total_errors = 0

    for suite in suites:
        for tc in suite.findall("testcase"):
            name = tc.get("name", "unknown")
            time_seconds = float(tc.get("time", "0"))

            failure = tc.find("failure")
            error = tc.find("error")

            if failure is not None:
                message = failure.get("message", failure.text or "")
                passed = False
            elif error is not None:
                message = error.get("message", error.text or "")
                passed = False
                total_errors += 1
            else:
                message = None
                passed = True

            entry = {"name": name, "passed": passed, "time_seconds": time_seconds}
            if message is not None:
                entry["message"] = message
            tests.append(entry)

    total = len(tests)
    passed = sum(1 for t in tests if t["passed"])
    failed = total - passed - total_errors

    total_time = sum(t["time_seconds"] for t in tests)

    return {
        "tests": tests,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": total_errors,
            "time_seconds": round(total_time, 3),
        },
    }


def _empty_summary() -> dict:
    return {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "time_seconds": 0.0,
    }
