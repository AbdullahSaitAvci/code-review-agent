"""Quick smoke-test: read bad_example.py and run it through review_code."""
import io
import sys
from pathlib import Path

# Allow running from the project root or from tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Force UTF-8 output so emoji/non-ASCII chars from the review print correctly.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from agent.core import review_code

BAD_EXAMPLE = Path(__file__).parent / "sample_code" / "bad_example.py"


def main() -> None:
    code = BAD_EXAMPLE.read_text(encoding="utf-8")
    print(f"--- Sending {BAD_EXAMPLE.name} to review_code ---\n")

    result = review_code(code)

    if result["success"]:
        print(f"Tools used: {result['tools_used']}\n")
        print("=== Review ===")
        print(result["review"])
    else:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
