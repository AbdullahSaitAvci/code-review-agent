import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.tools import read_python_file

SAMPLE_DIR = Path(__file__).parent / "sample_code"
BAD_EXAMPLE = SAMPLE_DIR / "bad_example.py"


def test_reads_existing_file():
    result = read_python_file(str(BAD_EXAMPLE))
    assert result["success"] is True
    assert "content" in result
    assert len(result["content"]) > 0


def test_content_contains_expected_code():
    result = read_python_file(str(BAD_EXAMPLE))
    assert result["success"] is True
    assert "def calculate" in result["content"]
    assert "def process" in result["content"]


def test_returns_absolute_file_path():
    result = read_python_file(str(BAD_EXAMPLE))
    assert result["success"] is True
    assert Path(result["file_path"]).is_absolute()


def test_file_not_found():
    result = read_python_file("/nonexistent/path/missing.py")
    assert result["success"] is False
    assert "error" in result
    assert "not found" in result["error"].lower()


def test_rejects_non_python_file():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"hello world")
        tmp_path = f.name
    try:
        result = read_python_file(tmp_path)
        assert result["success"] is False
        assert "error" in result
    finally:
        os.unlink(tmp_path)


def test_rejects_directory_path():
    result = read_python_file(str(SAMPLE_DIR))
    assert result["success"] is False
    assert "error" in result


def test_reads_temp_python_file():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("x = 1\n")
        tmp_path = f.name
    try:
        result = read_python_file(tmp_path)
        assert result["success"] is True
        assert "x = 1" in result["content"]
    finally:
        os.unlink(tmp_path)
