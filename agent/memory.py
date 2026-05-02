from typing import Any


def new_session() -> list[dict[str, Any]]:
    """Return an empty messages list for a fresh review session."""
    return []


def add_user_message(messages: list[dict[str, Any]], content: str) -> None:
    """Append a user-role message to *messages* in-place."""
    messages.append({"role": "user", "content": content})


def add_assistant_message(messages: list[dict[str, Any]], content: str) -> None:
    """Append an assistant-role message to *messages* in-place."""
    messages.append({"role": "assistant", "content": content})


def get_history(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the current message list."""
    return messages
