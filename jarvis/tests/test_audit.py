"""Tests for the append-only audit log."""

from __future__ import annotations

import importlib

from jarvis import audit


def test_log_then_tail() -> None:
    importlib.reload(audit)
    audit.log_tool_call("notify", {"title": "x", "message": "y"}, "ok")
    audit.log_tool_call("market_status", {"market": "forex"}, "open")
    rows = audit.tail(10)
    assert len(rows) == 2
    assert rows[-1]["tool"] == "market_status"
    assert rows[0]["args"]["title"] == "x"


def test_truncation() -> None:
    importlib.reload(audit)
    audit.log_tool_call("big", {}, "x" * 5000)
    row = audit.tail(1)[0]
    assert row["result"].endswith("…")
    assert len(row["result"]) <= 1100


def test_swallows_unserializable() -> None:
    importlib.reload(audit)

    class NotJSON:
        def __repr__(self) -> str:
            return "<NotJSON>"

    audit.log_tool_call("weird", {"obj": NotJSON()}, NotJSON())
    rows = audit.tail(1)
    assert rows[0]["tool"] == "weird"
