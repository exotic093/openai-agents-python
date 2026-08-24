"""Tests for the .env round-trip in the auth helper."""

from __future__ import annotations

from pathlib import Path

import pytest

from jarvis import auth


@pytest.fixture
def tmp_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    env = tmp_path / ".env"
    monkeypatch.setattr(auth, "ENV_PATH", env)
    return env


def test_find_resolves_aliases() -> None:
    assert auth._find("gcal").name == "google_calendar"
    assert auth._find("mt5").name == "metatrader5"
    assert auth._find("qbo").name == "quickbooks"
    assert auth._find("nonexistent") is None


def test_write_env_creates_file_when_missing(tmp_env: Path) -> None:
    auth._write_env({"NOTION_API_TOKEN": "secret_abc"})
    text = tmp_env.read_text()
    assert "NOTION_API_TOKEN=secret_abc" in text


def test_write_env_preserves_existing_keys(tmp_env: Path) -> None:
    tmp_env.write_text("OPENAI_API_KEY=sk-keep\n# comment\nJARVIS_USER=Sir\n")
    auth._write_env({"NOTION_API_TOKEN": "tok"})
    parsed = auth._read_env()
    assert parsed == {
        "OPENAI_API_KEY": "sk-keep",
        "JARVIS_USER": "Sir",
        "NOTION_API_TOKEN": "tok",
    }
    # Comment must survive.
    assert "# comment" in tmp_env.read_text()


def test_write_env_updates_existing_in_place(tmp_env: Path) -> None:
    tmp_env.write_text("JARVIS_USER=old\nFOO=bar\n")
    auth._write_env({"JARVIS_USER": "Sir"})
    text = tmp_env.read_text()
    # The original line is rewritten where it was, not duplicated at the end.
    assert text.count("JARVIS_USER=") == 1
    assert "JARVIS_USER=Sir" in text
    assert "FOO=bar" in text


def test_run_with_unknown_returns_error(tmp_env: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = auth.run("not-a-real-integration")
    assert rc == 1


def test_run_without_args_lists(tmp_env: Path) -> None:
    rc = auth.run(None)
    assert rc == 0
