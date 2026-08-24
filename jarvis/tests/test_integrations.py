"""Tests for the MCP integration registry."""

from __future__ import annotations

import importlib

import pytest

from jarvis import integrations


def test_registry_contains_expected_integrations() -> None:
    names = {i.name for i in integrations.REGISTRY}
    assert {
        "gmail",
        "outlook",
        "google_calendar",
        "calendly",
        "slack",
        "whatsapp",
        "telegram",
        "notion",
        "tradingview",
        "metatrader5",
        "broker_http",
        "hubspot",
        "quickbooks",
    } == names


def test_skip_when_env_missing() -> None:
    importlib.reload(integrations)
    assert integrations.build_servers() == []
    report = integrations.status_report()
    assert "inactive" in report


def test_active_when_env_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOTION_API_TOKEN", "secret_test")
    importlib.reload(integrations)
    servers = integrations.build_servers()
    assert any(getattr(s, "name", "") == "notion" for s in servers)
    assert "notion" in integrations.status_report()


def test_http_integration_uses_streamable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALENDLY_API_TOKEN", "tok")
    monkeypatch.setenv("CALENDLY_MCP_URL", "https://example.com/mcp")
    importlib.reload(integrations)
    servers = integrations.build_servers()
    calendly = next(s for s in servers if getattr(s, "name", "") == "calendly")
    assert type(calendly).__name__ == "MCPServerStreamableHttp"


def test_optional_env_does_not_block_activation(monkeypatch: pytest.MonkeyPatch) -> None:
    """SLACK_CHANNEL_IDS is optional — slack should still activate without it."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-x")
    monkeypatch.setenv("SLACK_TEAM_ID", "T1")
    importlib.reload(integrations)
    assert any(getattr(s, "name", "") == "slack" for s in integrations.build_servers())
