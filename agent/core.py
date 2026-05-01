import json
import os
from typing import Any

import anthropic
from dotenv import load_dotenv

from agent.prompts import SYSTEM_PROMPT
from agent.tools import (
    ANALYZE_COMPLEXITY_SCHEMA,
    GET_USER_PROFILE_SCHEMA,
    READ_PYTHON_FILE_SCHEMA,
    RUN_STATIC_ANALYSIS_SCHEMA,
    UPDATE_USER_PROFILE_SCHEMA,
    analyze_complexity,
    get_user_profile,
    read_python_file,
    run_static_analysis,
    update_user_profile,
)

load_dotenv()

_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 16000
_MAX_ITERATIONS = 20

_TOOLS: list[dict] = [
    READ_PYTHON_FILE_SCHEMA,
    RUN_STATIC_ANALYSIS_SCHEMA,
    ANALYZE_COMPLEXITY_SCHEMA,
    GET_USER_PROFILE_SCHEMA,
    UPDATE_USER_PROFILE_SCHEMA,
]

_TOOL_FUNCTIONS: dict[str, Any] = {
    "read_python_file": read_python_file,
    "run_static_analysis": run_static_analysis,
    "analyze_complexity": analyze_complexity,
    "get_user_profile": get_user_profile,
    "update_user_profile": update_user_profile,
}


def _dispatch_tool(name: str, tool_input: dict) -> str:
    """Execute the Python function for *name* and return its result as JSON."""
    fn = _TOOL_FUNCTIONS.get(name)
    if fn is None:
        return json.dumps({"success": False, "error": f"Unknown tool: {name}"})
    try:
        result = fn(**tool_input)
    except Exception as exc:  # noqa: BLE001
        result = {"success": False, "error": str(exc)}
    return json.dumps(result, ensure_ascii=False)


def review_code(code: str) -> dict:
    """Analyse *code* with an agentic loop and return a structured review dict.

    Returns:
        {
            "success": bool,
            "review": str,        # Claude's final Markdown review (on success)
            "tools_used": list,   # Tool names called during the loop
            "error": str,         # Only present on failure
        }
    """
    if not code or not code.strip():
        return {"success": False, "error": "Empty code string.", "tools_used": []}

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"success": False, "error": "ANTHROPIC_API_KEY not set.", "tools_used": []}

    client = anthropic.Anthropic(api_key=api_key)

    messages: list[dict] = [
        {
            "role": "user",
            "content": (
                "Lütfen aşağıdaki Python kodunu incele:\n\n"
                f"```python\n{code}\n```"
            ),
        }
    ]

    tools_used: list[str] = []

    for _ in range(_MAX_ITERATIONS):
        response = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=_TOOLS,
            messages=messages,
        )

        # Preserve the full content list so tool_use blocks are retained.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            review_text = next(
                (block.text for block in response.content if block.type == "text"),
                "",
            )
            return {
                "success": True,
                "review": review_text,
                "tools_used": tools_used,
            }

        if response.stop_reason != "tool_use":
            return {
                "success": False,
                "error": f"Unexpected stop reason: {response.stop_reason}",
                "tools_used": tools_used,
            }

        # Execute every tool_use block and collect results.
        tool_results: list[dict] = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            tools_used.append(block.name)
            result_json = _dispatch_tool(block.name, block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_json,
                }
            )

        messages.append({"role": "user", "content": tool_results})

    return {
        "success": False,
        "error": f"Agent loop exceeded {_MAX_ITERATIONS} iterations without end_turn.",
        "tools_used": tools_used,
    }
