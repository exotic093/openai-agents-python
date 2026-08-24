"""Open URLs and local files in the user's default applications."""

from __future__ import annotations

import platform
import subprocess
import webbrowser
from pathlib import Path

from agents import function_tool


@function_tool
def open_url(url: str) -> str:
    """Open a URL in the user's default browser."""
    try:
        webbrowser.open(url, new=2)
        return f"Opened {url}"
    except Exception as e:
        return f"Failed to open URL: {e}"


@function_tool
def open_path(path: str) -> str:
    """Open a local file or folder using the OS default handler."""
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Path not found: {p}"
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", str(p)])
        elif system == "Windows":
            subprocess.Popen(["cmd", "/c", "start", "", str(p)], shell=False)
        else:
            subprocess.Popen(["xdg-open", str(p)])
        return f"Opened {p}"
    except Exception as e:
        return f"Failed to open path: {e}"
