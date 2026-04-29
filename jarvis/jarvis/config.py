"""Runtime configuration for Jarvis."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.environ.get("JARVIS_DATA_DIR", Path.home() / ".jarvis"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_DB = DATA_DIR / "memory.db"
SESSION_DB = DATA_DIR / "sessions.db"


@dataclass(frozen=True)
class Settings:
    user_name: str = os.environ.get("JARVIS_USER", os.environ.get("USER", "sir"))
    text_model: str = os.environ.get("JARVIS_MODEL", "gpt-5")
    voice_model: str = os.environ.get(
        "JARVIS_VOICE_MODEL", "gpt-realtime"
    )
    voice: str = os.environ.get("JARVIS_VOICE", "ballad")
    workspace: Path = Path(os.environ.get("JARVIS_WORKSPACE", Path.cwd()))
    allow_shell: bool = os.environ.get("JARVIS_ALLOW_SHELL", "1") == "1"


settings = Settings()
