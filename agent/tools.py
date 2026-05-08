import ast
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
        "findings (line, column, code, message) from both tools. "
        "For non-Python languages returns an empty result with a note."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The source code to analyse.",
            },
            "language": {
                "type": "string",
                "description": "Programming language of the code (python, javascript, java, etc.)",
                "default": "python",
            },
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


def run_static_analysis(code: str, language: str = "python") -> dict:
    """Write *code* to a temp file, run pylint + flake8, return combined findings."""
    if not code or not code.strip():
        return {"success": False, "error": "Empty code string."}

    if language.lower() != "python":
        return {
            "success": True,
            "pylint": [],
            "flake8": [],
            "total_issues": 0,
            "summary": {"pylint_count": 0, "flake8_count": 0},
            "note": "Statik analiz sadece Python için destekleniyor. Claude kendi analizi yapacak.",
        }

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


ANALYZE_COMPLEXITY_SCHEMA = {
    "name": "analyze_complexity",
    "description": (
        "Parses a Python code string with the ast module and returns per-function "
        "metrics: line count, maximum nesting depth (if/for/while/with blocks), "
        "and parameter count."
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


def _nesting_depth(node: ast.AST) -> int:
    """Return the maximum nesting depth of control-flow blocks inside *node*."""
    NESTING_NODES = (ast.If, ast.For, ast.While, ast.With)

    def _walk(n: ast.AST, depth: int) -> int:
        max_depth = depth
        for child in ast.iter_child_nodes(n):
            if isinstance(child, NESTING_NODES):
                max_depth = max(max_depth, _walk(child, depth + 1))
            else:
                max_depth = max(max_depth, _walk(child, depth))
        return max_depth

    return _walk(node, 0)


def analyze_complexity(code: str) -> dict:
    """Parse *code* with ast and return per-function complexity metrics."""
    if not code or not code.strip():
        return {"success": False, "error": "Empty code string."}

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {"success": False, "error": f"Syntax error: {exc}"}

    functions = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        start = node.lineno
        end = max(
            (getattr(child, "end_lineno", start) for child in ast.walk(node)),
            default=start,
        )
        line_count = end - start + 1
        param_count = len(node.args.args) + len(node.args.posonlyargs) + len(node.args.kwonlyargs)
        if node.args.vararg:
            param_count += 1
        if node.args.kwarg:
            param_count += 1

        functions.append(
            {
                "name": node.name,
                "start_line": start,
                "end_line": end,
                "line_count": line_count,
                "nesting_depth": _nesting_depth(node),
                "param_count": param_count,
            }
        )

    return {
        "success": True,
        "function_count": len(functions),
        "functions": functions,
    }


_PROFILE_PATH = Path(__file__).parent.parent / "data" / "user_profile.json"

_DEFAULT_PROFILE: dict = {
    "recurring_issues": {},
    "preferences": {"style_guide": "PEP8", "verbosity": "detailed"},
    "review_count": 0,
}


def _load_profile() -> dict:
    """Read user_profile.json, returning defaults if the file is missing or corrupt."""
    if not _PROFILE_PATH.exists():
        return _DEFAULT_PROFILE.copy()
    try:
        return json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _DEFAULT_PROFILE.copy()


def _save_profile(profile: dict) -> None:
    """Write *profile* back to user_profile.json."""
    _PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _PROFILE_PATH.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")


GET_USER_PROFILE_SCHEMA = {
    "name": "get_user_profile",
    "description": (
        "Returns the persistent user profile stored in data/user_profile.json. "
        "Includes recurring_issues counters, preferences, and total review_count."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}


def get_user_profile() -> dict:
    """Read and return the user profile from disk."""
    try:
        profile = _load_profile()
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": str(exc)}
    return {"success": True, "profile": profile}


UPDATE_USER_PROFILE_SCHEMA = {
    "name": "update_user_profile",
    "description": (
        "Increments the recurring_issues counter for *issue_key* by 1 and "
        "increments review_count by 1, then persists the changes to disk."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "issue_key": {
                "type": "string",
                "description": (
                    "A short identifier for the recurring issue "
                    "(e.g. 'missing-docstring', 'line-too-long')."
                ),
            }
        },
        "required": ["issue_key"],
    },
}


def update_user_profile(issue_key: str) -> dict:
    """Increment the counter for *issue_key* and review_count, then save."""
    if not issue_key or not issue_key.strip():
        return {"success": False, "error": "issue_key must be a non-empty string."}

    try:
        profile = _load_profile()
        profile.setdefault("recurring_issues", {})
        profile["recurring_issues"][issue_key] = profile["recurring_issues"].get(issue_key, 0) + 1
        profile["review_count"] = profile.get("review_count", 0) + 1
        _save_profile(profile)
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": str(exc)}

    return {
        "success": True,
        "issue_key": issue_key,
        "new_count": profile["recurring_issues"][issue_key],
        "review_count": profile["review_count"],
    }
