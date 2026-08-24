"""File-system tools, scoped to the configured workspace."""

from __future__ import annotations

from pathlib import Path

from agents import function_tool

from ..config import settings

MAX_READ_BYTES = 200_000


def _resolve(path: str) -> Path:
    p = (settings.workspace / path).expanduser().resolve()
    workspace = settings.workspace.resolve()
    if not str(p).startswith(str(workspace)):
        raise ValueError(
            f"Path {p} is outside the workspace {workspace}. "
            "Set JARVIS_WORKSPACE to broaden access."
        )
    return p


@function_tool
def read_file(path: str) -> str:
    """Read a UTF-8 text file from the workspace and return its contents."""
    try:
        p = _resolve(path)
    except ValueError as e:
        return str(e)
    if not p.exists():
        return f"File not found: {p}"
    if p.is_dir():
        return f"{p} is a directory; use list_dir."
    data = p.read_bytes()[:MAX_READ_BYTES]
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return f"(binary file, {len(data)} bytes — refusing to decode)"


@function_tool
def write_file(path: str, content: str, overwrite: bool = False) -> str:
    """Write text content to a file inside the workspace.

    Args:
        path: Path relative to the workspace.
        content: The full new content of the file.
        overwrite: If False and the file already exists, refuse.
    """
    try:
        p = _resolve(path)
    except ValueError as e:
        return str(e)
    if p.exists() and not overwrite:
        return f"Refusing to overwrite existing file: {p} (set overwrite=True)"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {p}"


@function_tool
def list_dir(path: str = ".") -> str:
    """List entries in a directory inside the workspace."""
    try:
        p = _resolve(path)
    except ValueError as e:
        return str(e)
    if not p.exists():
        return f"Not found: {p}"
    if not p.is_dir():
        return f"{p} is not a directory."
    entries = []
    for child in sorted(p.iterdir()):
        kind = "DIR " if child.is_dir() else "FILE"
        entries.append(f"{kind}  {child.name}")
    return "\n".join(entries) or "(empty)"
