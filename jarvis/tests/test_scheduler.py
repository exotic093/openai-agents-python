"""Tests for the persistent task scheduler."""

from __future__ import annotations

import importlib

from jarvis import scheduler


def test_add_list_remove() -> None:
    importlib.reload(scheduler)
    scheduler.add("brief", 3600, "Give me my morning brief.")
    tasks = scheduler.list_tasks()
    assert any(t.name == "brief" and t.every_seconds == 3600 for t in tasks)

    scheduler.remove("brief")
    assert all(t.name != "brief" for t in scheduler.list_tasks())


def test_toggle() -> None:
    importlib.reload(scheduler)
    scheduler.add("ping", 60, "Ping me.")
    scheduler.toggle("ping", enabled=False)
    assert all(t.enabled == 0 for t in scheduler.list_tasks() if t.name == "ping")
    scheduler.toggle("ping", enabled=True)
    assert all(t.enabled == 1 for t in scheduler.list_tasks() if t.name == "ping")


def test_due_respects_interval() -> None:
    importlib.reload(scheduler)
    scheduler.add("hourly", 3600, "x")
    # Just-added task has last_run=0, so it's due immediately.
    assert any(t.name == "hourly" for t in scheduler._due())
    scheduler._mark_ran("hourly")
    # Now it's not due for another 3600s.
    assert all(t.name != "hourly" for t in scheduler._due())
