import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


READ_PYTHON_FILE_SCHEMA = {
    "name": "read_python_file",
    "description": "Reads a Python source file from disk and returns its content as a string.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute or relative path to the .py file to read.",
            }
        },
        "required": ["file_path"],
    },
}


def read_python_file(file_path: str) -> dict:
    """Read a Python file and return its content or a structured error."""
    path = Path(file_path)

    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    if not path.is_file():
        return {"success": False, "error": f"Path is not a file: {file_path}"}

    if path.suffix != ".py":
        return {"success": False, "error": f"Not a Python file: {file_path}"}

    try:
        content = path.read_text(encoding="utf-8")
    except PermissionError:
        return {"success": False, "error": f"Permission denied: {file_path}"}
    except OSError as exc:
        return {"success": False, "error": f"Could not read file: {exc}"}

    return {"success": True, "content": content, "file_path": str(path.resolve())}


RUN_STATIC_ANALYSIS_SCHEMA = {
    "name": "run_static_analysis",
    "description": (
        "Runs pylint and flake8 on a Python code string and returns structured "
        "findings (line, column, code, message) from both tools."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python source code to analyse.",
            }
        },
        "required": ["code"],
    },
}

_TIMEOUT = 15


def _run_pylint(path: str) -> list[dict]:
    """Run pylint on *path* and return a list of issue dicts."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pylint", "--output-format=json", path],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return [{"tool": "pylint", "error": "timeout"}]
    except FileNotFoundError:
        return [{"tool": "pylint", "error": "pylint not installed"}]

    try:
        raw = json.loads(proc.stdout) if proc.stdout.strip() else []
    except json.JSONDecodeError:
        raw = []

    return [
        {
            "tool": "pylint",
            "line": item.get("line"),
            "column": item.get("column"),
            "code": item.get("message-id"),
            "symbol": item.get("symbol"),
            "message": item.get("message"),
            "type": item.get("type"),
        }
        for item in raw
    ]


def _run_flake8(path: str) -> list[dict]:
    """Run flake8 on *path* and return a list of issue dicts."""
    fmt = "%(path)s:%(row)d:%(col)d: %(code)s %(text)s"
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "flake8", f"--format={fmt}", path],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return [{"tool": "flake8", "error": "timeout"}]
    except FileNotFoundError:
        return [{"tool": "flake8", "error": "flake8 not installed"}]

    issues = []
    pattern = re.compile(r"^.+?:(\d+):(\d+):\s+([A-Z]\d+)\s+(.+)$")
    for line in proc.stdout.splitlines():
        m = pattern.match(line)
        if m:
            issues.append(
                {
                    "tool": "flake8",
                    "line": int(m.group(1)),
                    "column": int(m.group(2)),
                    "code": m.group(3),
                    "message": m.group(4),
                }
            )
    return issues


def run_static_analysis(code: str) -> dict:
    """Write *code* to a temp file, run pylint + flake8, return combined findings."""
    if not code or not code.strip():
        return {"success": False, "error": "Empty code string."}

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        pylint_issues = _run_pylint(tmp_path)
        flake8_issues = _run_flake8(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    all_issues = pylint_issues + flake8_issues
    return {
        "success": True,
        "pylint": pylint_issues,
        "flake8": flake8_issues,
        "total_issues": len(all_issues),
        "summary": {
            "pylint_count": len(pylint_issues),
            "flake8_count": len(flake8_issues),
        },
    }
