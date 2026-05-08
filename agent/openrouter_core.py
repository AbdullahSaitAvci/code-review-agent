import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

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

_BASE_URL = "https://openrouter.ai/api/v1"
_MAX_ITERATIONS = 20

_TOOL_FUNCTIONS: dict[str, Any] = {
    "read_python_file": read_python_file,
    "run_static_analysis": run_static_analysis,
    "analyze_complexity": analyze_complexity,
    "get_user_profile": get_user_profile,
    "update_user_profile": update_user_profile,
}


def _to_openai_tool(schema: dict) -> dict:
    """Convert an Anthropic-style tool schema to OpenAI function calling format."""
    return {
        "type": "function",
        "function": {
            "name": schema["name"],
            "description": schema["description"],
            "parameters": schema["input_schema"],
        },
    }


_TOOLS: list[dict] = [
    _to_openai_tool(READ_PYTHON_FILE_SCHEMA),
    _to_openai_tool(RUN_STATIC_ANALYSIS_SCHEMA),
    _to_openai_tool(ANALYZE_COMPLEXITY_SCHEMA),
    _to_openai_tool(GET_USER_PROFILE_SCHEMA),
    _to_openai_tool(UPDATE_USER_PROFILE_SCHEMA),
]


def _dispatch_tool(name: str, arguments_json: str) -> str:
    """Parse *arguments_json*, call the matching Python function, return JSON result."""
    fn = _TOOL_FUNCTIONS.get(name)
    if fn is None:
        return json.dumps({"success": False, "error": f"Unknown tool: {name}"})
    try:
        result = fn(**json.loads(arguments_json))
    except Exception as exc:  # noqa: BLE001
        result = {"success": False, "error": str(exc)}
    return json.dumps(result, ensure_ascii=False)


def review_code(
    code: str,
    model: str = "deepseek/deepseek-r1-0528:free",
    language: str = "python",
) -> dict:
    """Run an agentic loop with the given OpenRouter model and return a review dict.

    Returns the same shape as agent.core.review_code:
        {"success": bool, "review": str, "tools_used": list, "error": str}
    """
    if not code or not code.strip():
        return {"success": False, "error": "Empty code string.", "tools_used": []}

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"success": False, "error": "OPENROUTER_API_KEY not set.", "tools_used": []}

    client = OpenAI(api_key=api_key, base_url=_BASE_URL)

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Lütfen aşağıdaki {language} kodunu incele:\n\n"
                f"```{language}\n{code}\n```"
            ),
        },
    ]

    tools_used: list[str] = []

    for _ in range(_MAX_ITERATIONS):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=_TOOLS,
                tool_choice="auto",
            )
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc), "tools_used": tools_used}

        if not response or not response.choices:
            return {"success": False, "error": "Model boş yanıt döndürdü.", "tools_used": tools_used}

        choice = response.choices[0]
        finish_reason = choice.finish_reason

        if finish_reason == "stop":
            return {
                "success": True,
                "review": choice.message.content or "",
                "tools_used": tools_used,
            }

        if finish_reason != "tool_calls":
            return {
                "success": False,
                "error": f"Unexpected finish_reason: {finish_reason}",
                "tools_used": tools_used,
            }

        tool_calls = choice.message.tool_calls or []
        messages.append({
            "role": "assistant",
            "content": choice.message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        })

        for tc in tool_calls:
            tools_used.append(tc.function.name)
            result_json = _dispatch_tool(tc.function.name, tc.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_json,
            })

    return {
        "success": False,
        "error": f"Agent loop exceeded {_MAX_ITERATIONS} iterations without stop.",
        "tools_used": tools_used,
    }
