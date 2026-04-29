"""System-level tools: time, OS info, shell execution."""

from __future__ import annotations

import datetime as _dt
import platform
import shlex
import subprocess

from agents import function_tool

from ..config import settings


@function_tool
def get_time(timezone: str | None = None) -> str:
    """Return the current local date and time.

    Args:
        timezone: Optional IANA timezone (e.g. "America/New_York"). If omitted,
            uses the host's local time.
    """
    if timezone:
        try:
            from zoneinfo import ZoneInfo

            now = _dt.datetime.now(ZoneInfo(timezone))
        except Exception as e:
            return f"Could not resolve timezone {timezone!r}: {e}"
    else:
        now = _dt.datetime.now().astimezone()
    return now.strftime("%A, %B %d %Y — %H:%M:%S %Z").strip()


@function_tool
def system_info() -> str:
    """Report basic information about the host machine."""
    return (
        f"OS: {platform.system()} {platform.release()}\n"
        f"Machine: {platform.machine()}\n"
        f"Python: {platform.python_version()}\n"
        f"Node: {platform.node()}\n"
        f"User: {settings.user_name}"
    )


@function_tool
def run_shell(command: str, timeout_s: int = 30) -> str:
    """Run a shell command on the host and return combined stdout/stderr.

    Disabled when JARVIS_ALLOW_SHELL=0. Use carefully — this executes on the
    user's machine.
    """
    if not settings.allow_shell:
        return "Shell access is disabled (set JARVIS_ALLOW_SHELL=1 to enable)."
    try:
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=settings.workspace,
        )
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout_s}s."
    except FileNotFoundError as e:
        return f"Command not found: {e}"
    out = (result.stdout or "") + (result.stderr or "")
    return f"[exit {result.returncode}]\n{out.strip()}"[:8000]
