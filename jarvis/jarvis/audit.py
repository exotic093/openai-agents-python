"""Append-only audit log of every tool call Jarvis makes.

Every tool invocation is recorded as a single JSON line in
`~/.jarvis/audit.log` with timestamp, tool name, args, and a truncated
result. Useful for reviewing what Jarvis did on your behalf.
"""

from __future__ import annotations

import json
import time
from typing import Any

from .config import DATA_DIR

AUDIT_PATH = DATA_DIR / "audit.log"


def log_tool_call(tool_name: str, args: dict[str, Any], result: Any) -> None:
    record = {
        "ts": time.time(),
        "tool": tool_name,
        "args": _safe(args),
        "result": _truncate(_safe(result), 1000),
    }
    try:
        with AUDIT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except Exception:
        # Audit must never break the agent; swallow silently.
        pass


def tail(n: int = 50) -> list[dict[str, Any]]:
    if not AUDIT_PATH.exists():
        return []
    lines = AUDIT_PATH.read_text(encoding="utf-8").splitlines()[-n:]
    out: list[dict[str, Any]] = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _safe(value: Any) -> Any:
    try:
        json.dumps(value, default=str)
        return value
    except (TypeError, ValueError):
        return str(value)


def _truncate(value: Any, limit: int) -> Any:
    s = value if isinstance(value, str) else json.dumps(value, default=str)
    return s if len(s) <= limit else s[:limit] + "…"
