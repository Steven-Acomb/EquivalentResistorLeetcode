"""FastAPI application for the local problem workbench."""

import asyncio
import json
import os
from pathlib import Path

import markdown
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from engine import run_solution

app = FastAPI(title="Problem Workbench")

# Resolve paths
_SERVER_DIR = Path(__file__).parent.resolve()
_STATIC_DIR = _SERVER_DIR / "static"
_PROJECT_ROOT = _SERVER_DIR.parent
_PROBLEMS_DIR = _PROJECT_ROOT / "problems"
_SOLUTIONS_DIR = _PROJECT_ROOT / "solutions"

# Hardcoded for now — single problem
_PROBLEM_SLUG = "equivalent-resistance"


# --- Request/response models ---

class RunRequest(BaseModel):
    language: str
    code: str


class SolutionBody(BaseModel):
    code: str


# --- API routes ---

@app.get("/api/problem")
async def get_problem():
    """Return problem metadata, rendered description HTML, and available languages."""
    problem_dir = _PROBLEMS_DIR / _PROBLEM_SLUG

    # Render problem.md to HTML
    problem_md_path = problem_dir / "problem.md"
    if not problem_md_path.is_file():
        raise HTTPException(status_code=404, detail="problem.md not found")

    md_text = problem_md_path.read_text()
    description_html = markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables", "codehilite"],
    )

    # Discover languages
    languages_dir = problem_dir / "languages"
    languages = []
    if languages_dir.is_dir():
        for lang_dir in sorted(languages_dir.iterdir()):
            runner_json = lang_dir / "runner.json"
            if not runner_json.is_file():
                continue

            config = json.loads(runner_json.read_text())
            solution_file = config["solution_file"]
            stub_path = lang_dir / solution_file

            stub_code = stub_path.read_text() if stub_path.is_file() else ""

            languages.append({
                "name": lang_dir.name,
                "stub": stub_code,
                "solution_file": solution_file,
            })

    # Load test case metadata
    tests_meta = []
    testcases_path = problem_dir / "testcases.json"
    if testcases_path.is_file():
        testcases = json.loads(testcases_path.read_text())
        for tc in testcases.get("tests", []):
            # Build a display-friendly target
            target = tc.get("targetResistance")
            if isinstance(target, dict) and target.get("type") == "evaluateConfig":
                target_display = f'evaluateConfig("{target["config"]}")'
            elif target == "MAX":
                target_display = "MAX (infinity)"
            else:
                target_display = str(target)

            tests_meta.append({
                "id": tc["id"],
                "description": tc.get("description", ""),
                "num_base_resistances": len(tc.get("baseResistances", [])),
                "target_resistance": target_display,
                "max_resistors": tc.get("maxResistors"),
            })

    return {
        "problem": _PROBLEM_SLUG,
        "description_html": description_html,
        "languages": languages,
        "tests": tests_meta,
    }


@app.post("/api/run")
async def run_tests(req: RunRequest):
    """Run solution code against the test harness."""
    # Validate language exists
    lang_dir = _PROBLEMS_DIR / _PROBLEM_SLUG / "languages" / req.language
    if not lang_dir.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Unknown language: {req.language}",
        )

    # Run engine in thread pool to avoid blocking the server
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: run_solution(
            problem=_PROBLEM_SLUG,
            language=req.language,
            solution_code=req.code,
        ),
    )

    return result


@app.get("/api/solution/{language}")
async def get_solution(language: str):
    """Return saved solution if exists, otherwise the stub."""
    lang_dir = _PROBLEMS_DIR / _PROBLEM_SLUG / "languages" / language
    if not lang_dir.is_dir():
        raise HTTPException(status_code=400, detail=f"Unknown language: {language}")

    config = json.loads((lang_dir / "runner.json").read_text())
    solution_file = config["solution_file"]

    # Check for saved solution first
    saved_path = _SOLUTIONS_DIR / _PROBLEM_SLUG / language / Path(solution_file).name
    if saved_path.is_file():
        return {
            "code": saved_path.read_text(),
            "source": "saved",
        }

    # Fall back to stub
    stub_path = lang_dir / solution_file
    return {
        "code": stub_path.read_text() if stub_path.is_file() else "",
        "source": "stub",
    }


@app.put("/api/solution/{language}")
async def save_solution(language: str, body: SolutionBody):
    """Save solution code to the solutions directory."""
    lang_dir = _PROBLEMS_DIR / _PROBLEM_SLUG / "languages" / language
    if not lang_dir.is_dir():
        raise HTTPException(status_code=400, detail=f"Unknown language: {language}")

    config = json.loads((lang_dir / "runner.json").read_text())
    solution_file = config["solution_file"]

    saved_path = _SOLUTIONS_DIR / _PROBLEM_SLUG / language / Path(solution_file).name
    saved_path.parent.mkdir(parents=True, exist_ok=True)
    saved_path.write_text(body.code)

    return {"status": "saved", "path": str(saved_path.relative_to(_PROJECT_ROOT))}


@app.delete("/api/solution/{language}")
async def delete_solution(language: str):
    """Delete saved solution (reset to stub)."""
    lang_dir = _PROBLEMS_DIR / _PROBLEM_SLUG / "languages" / language
    if not lang_dir.is_dir():
        raise HTTPException(status_code=400, detail=f"Unknown language: {language}")

    config = json.loads((lang_dir / "runner.json").read_text())
    solution_file = config["solution_file"]

    saved_path = _SOLUTIONS_DIR / _PROBLEM_SLUG / language / Path(solution_file).name
    if saved_path.is_file():
        saved_path.unlink()

    return {"status": "deleted"}


# --- Static files (must be last — catch-all mount) ---

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/")
async def index():
    """Serve the main workbench page."""
    return FileResponse(str(_STATIC_DIR / "index.html"))
