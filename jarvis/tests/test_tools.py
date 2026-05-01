"""Tests for built-in tools — focused on non-network behavior."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from jarvis import config


def _invoke(tool, **kwargs) -> str:
    """Call a `@function_tool`-decorated callable synchronously.

    The Agents SDK wraps these in `FunctionTool`; we drop down to the
    underlying Python callable for unit tests.
    """
    fn = getattr(tool, "on_invoke_tool", None) or tool
    if hasattr(tool, "on_invoke_tool"):
        # Real tools expose the original callable on `params_json_schema`-aware
        # wrappers; for unit tests just go via the public `__wrapped__`.
        fn = tool.__wrapped__  # type: ignore[attr-defined]
    return fn(**kwargs)


def _call(tool, **kwargs):
    """Reach the original function under @function_tool."""
    # The decorator stores the callable as `func` on FunctionTool, but we
    # registered them as plain decorated callables — simplest path is to use
    # the JSON-tool invoke path.
    import asyncio

    schema_call = tool.on_invoke_tool
    return asyncio.run(schema_call(None, json.dumps(kwargs)))


def test_get_time_returns_string() -> None:
    from jarvis.tools.system import get_time

    out = _call(get_time)
    assert isinstance(out, str)
    assert len(out) > 0


def test_system_info_includes_user(monkeypatch: pytest.MonkeyPatch) -> None:
    importlib.reload(config)
    from jarvis.tools.system import system_info

    out = _call(system_info)
    assert "Sir" in out


def test_run_shell_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JARVIS_ALLOW_SHELL", "0")
    importlib.reload(config)
    import jarvis.tools.system as s

    importlib.reload(s)
    out = _call(s.run_shell, command="echo hi")
    assert "disabled" in out.lower()


def test_read_write_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JARVIS_WORKSPACE", str(tmp_path))
    importlib.reload(config)
    import jarvis.tools.files as f

    importlib.reload(f)

    write_msg = _call(f.write_file, path="hello.txt", content="hi")
    assert "Wrote" in write_msg
    assert (tmp_path / "hello.txt").read_text() == "hi"

    out = _call(f.read_file, path="hello.txt")
    assert out == "hi"


def test_write_file_refuses_overwrite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JARVIS_WORKSPACE", str(tmp_path))
    importlib.reload(config)
    import jarvis.tools.files as f

    importlib.reload(f)
    _call(f.write_file, path="x.txt", content="a")
    out = _call(f.write_file, path="x.txt", content="b")
    assert "Refusing" in out
    out = _call(f.write_file, path="x.txt", content="b", overwrite=True)
    assert "Wrote" in out


def test_path_traversal_blocked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JARVIS_WORKSPACE", str(tmp_path))
    importlib.reload(config)
    import jarvis.tools.files as f

    importlib.reload(f)
    out = _call(f.read_file, path="../../etc/passwd")
    assert "outside the workspace" in out


def test_memory_tools_round_trip() -> None:
    import jarvis.memory as m
    import jarvis.tools.memory_tools as mt

    importlib.reload(m)
    importlib.reload(mt)
    _call(mt.remember, key="test.fact", value="value-X")
    out = _call(mt.recall, query="value-X")
    assert "value-X" in out
