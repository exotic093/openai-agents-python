"""Tests for the persistent SQLite memory store."""

from __future__ import annotations

import importlib

from jarvis import memory


def _fresh_store() -> memory.MemoryStore:
    importlib.reload(memory)
    return memory.MemoryStore()


def test_remember_and_recall() -> None:
    store = _fresh_store()
    store.remember("work.role", "trader")
    store.remember("hobbies.cats", "Two cats — top priority.")

    hits = store.recall("cats")
    assert len(hits) == 1
    assert hits[0].key == "hobbies.cats"


def test_all_returns_newest_first() -> None:
    store = _fresh_store()
    store.remember("a", "first")
    store.remember("b", "second")
    rows = store.all()
    assert [m.key for m in rows] == ["b", "a"]


def test_forget_removes_only_target() -> None:
    store = _fresh_store()
    keep = store.remember("keep", "y")
    drop = store.remember("drop", "y")
    assert store.forget(drop) is True
    keys = [m.key for m in store.all()]
    assert "drop" not in keys
    assert "keep" in keys
    assert store.forget(9999) is False
    _ = keep  # silence unused warning; covered by assertion above


def test_context_summary_handles_empty() -> None:
    store = _fresh_store()
    assert "no prior memories" in store.context_summary()
    store.remember("x", "y")
    assert "[x] y" in store.context_summary()
