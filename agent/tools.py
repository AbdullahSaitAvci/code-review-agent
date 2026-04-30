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
