"""Tests for the model provider selector + fallback chain."""

from __future__ import annotations

import importlib

import pytest

from jarvis import providers


def _reload_no_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip all provider keys and reload the module."""
    for var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "JARVIS_PROVIDER"]:
        monkeypatch.delenv(var, raising=False)
    importlib.reload(providers)


def test_selects_openai_when_only_openai_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _reload_no_keys(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    choice = providers.select()
    assert choice.name == "openai"
    assert choice.uses_litellm is False


def test_falls_back_to_claude_when_openai_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    _reload_no_keys(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    choice = providers.select()
    assert choice.name == "claude"
    assert choice.uses_litellm is True
    assert choice.model.startswith("anthropic/")


def test_falls_back_to_gemini_when_neither(monkeypatch: pytest.MonkeyPatch) -> None:
    _reload_no_keys(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "gm-x")
    choice = providers.select()
    assert choice.name == "gemini"
    assert choice.model.startswith("gemini/")


def test_preferred_provider_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    """JARVIS_PROVIDER should override the default order."""
    _reload_no_keys(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    monkeypatch.setenv("JARVIS_PROVIDER", "claude")
    assert providers.select().name == "claude"


def test_preferred_provider_still_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """If preferred provider has no key, we fall through to something that does."""
    _reload_no_keys(monkeypatch)
    monkeypatch.setenv("JARVIS_PROVIDER", "claude")
    monkeypatch.setenv("GEMINI_API_KEY", "gm-x")
    assert providers.select().name == "gemini"


def test_nothing_configured_returns_openai_default(monkeypatch: pytest.MonkeyPatch) -> None:
    _reload_no_keys(monkeypatch)
    assert providers.select().name == "openai"


def test_status_report_mentions_active(monkeypatch: pytest.MonkeyPatch) -> None:
    _reload_no_keys(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    report = providers.status_report()
    assert "claude" in report
    assert "anthropic" in report.lower()
