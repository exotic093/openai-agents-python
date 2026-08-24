"""Tools that let the agent read and write its own long-term memory."""

from __future__ import annotations

from agents import function_tool

from ..memory import get_store


@function_tool
def remember(key: str, value: str) -> str:
    """Store a fact for later recall.

    Args:
        key: A short topic label (e.g. "preferences", "wifi_password", "boss_name").
        value: The information to remember.
    """
    mem_id = get_store().remember(key, value)
    return f"Remembered (id={mem_id})."


@function_tool
def recall(query: str, limit: int = 10) -> str:
    """Search stored memories whose key or value contains the query string."""
    items = get_store().recall(query, limit=limit)
    if not items:
        return "(no memories matched)"
    return "\n".join(f"#{m.id} [{m.key}] {m.value}" for m in items)


@function_tool
def list_memories(limit: int = 25) -> str:
    """List the most recently stored memories."""
    items = get_store().all(limit=limit)
    if not items:
        return "(memory is empty)"
    return "\n".join(f"#{m.id} [{m.key}] {m.value}" for m in items)


@function_tool
def forget_memory(memory_id: int) -> str:
    """Delete a memory by its numeric id."""
    ok = get_store().forget(memory_id)
    return "Forgotten." if ok else f"No memory with id {memory_id}."
