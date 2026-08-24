"""Shared pytest fixtures: isolate Jarvis state per test."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated_jarvis(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point JARVIS_DATA_DIR + workspace at tmp_path and reload modules.

    Every test gets a clean memory database, sessions database, and workspace
    so they cannot pollute each other or the developer's `~/.jarvis`.
    """
    monkeypatch.setenv("JARVIS_DATA_DIR", str(tmp_path / "jarvis-data"))
    monkeypatch.setenv("JARVIS_WORKSPACE", str(tmp_path / "workspace"))
    monkeypatch.setenv("JARVIS_USER", "Sir")
    # Strip integration creds so tests run hermetic.
    for var in list(os.environ):
        if var.startswith(
            (
                "GMAIL_",
                "GCAL_",
                "MS365_",
                "CALENDLY_",
                "SLACK_",
                "WHATSAPP_",
                "TELEGRAM_",
                "NOTION_",
                "TRADINGVIEW_",
                "MT5_",
                "BROKER_MCP_",
                "HUBSPOT_",
                "QUICKBOOKS_",
            )
        ):
            monkeypatch.delenv(var, raising=False)

    # Reset module-level singletons / cached settings.
    import importlib

    import jarvis.config
    import jarvis.memory

    importlib.reload(jarvis.config)
    importlib.reload(jarvis.memory)
    return tmp_path
