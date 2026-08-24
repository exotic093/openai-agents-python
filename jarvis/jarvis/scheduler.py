"""Persistent task scheduler for proactive Jarvis behaviors.

Tasks live in SQLite at `~/.jarvis/scheduler.db` and have:
- A name (unique).
- A cron-ish "every" interval (seconds).
- A prompt that the agent runs when the task fires.

The `jarvis daemon` command runs a single-process loop that wakes up every
30 seconds and fires due tasks via the agent (with full integrations
attached). Results are written to the audit log.
"""

from __future__ import annotations

import asyncio
import sqlite3
import time
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from . import audit
from .config import DATA_DIR

DB_PATH = DATA_DIR / "scheduler.db"
console = Console()


@dataclass
class Task:
    name: str
    every_seconds: int
    prompt: str
    last_run: float
    enabled: int


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            name TEXT PRIMARY KEY,
            every_seconds INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            last_run REAL NOT NULL DEFAULT 0,
            enabled INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    conn.commit()
    return conn


def add(name: str, every_seconds: int, prompt: str) -> str:
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO tasks(name, every_seconds, prompt, last_run, enabled) "
            "VALUES (?, ?, ?, COALESCE((SELECT last_run FROM tasks WHERE name=?), 0), 1)",
            (name, every_seconds, prompt, name),
        )
    return f"task {name!r} scheduled every {every_seconds}s."


def remove(name: str) -> str:
    with _conn() as c:
        cur = c.execute("DELETE FROM tasks WHERE name = ?", (name,))
    return f"removed task {name!r}." if cur.rowcount else f"no task {name!r}."


def toggle(name: str, enabled: bool) -> str:
    with _conn() as c:
        cur = c.execute(
            "UPDATE tasks SET enabled = ? WHERE name = ?",
            (1 if enabled else 0, name),
        )
    return (
        f"{'enabled' if enabled else 'disabled'} {name!r}."
        if cur.rowcount
        else f"no task {name!r}."
    )


def list_tasks() -> list[Task]:
    with _conn() as c:
        rows = c.execute(
            "SELECT name, every_seconds, prompt, last_run, enabled FROM tasks ORDER BY name"
        ).fetchall()
    return [Task(*r) for r in rows]


def _due() -> list[Task]:
    now = time.time()
    return [t for t in list_tasks() if t.enabled and (now - t.last_run) >= t.every_seconds]


def _mark_ran(name: str) -> None:
    with _conn() as c:
        c.execute("UPDATE tasks SET last_run = ? WHERE name = ?", (time.time(), name))


def show() -> int:
    tasks = list_tasks()
    table = Table(title="scheduled tasks", show_header=True, header_style="bold")
    table.add_column("name")
    table.add_column("every")
    table.add_column("enabled")
    table.add_column("last_run")
    table.add_column("prompt")
    for t in tasks:
        last = "never" if t.last_run == 0 else _ago(t.last_run)
        table.add_row(
            t.name,
            _human_seconds(t.every_seconds),
            "yes" if t.enabled else "[dim]no[/]",
            last,
            t.prompt[:60] + ("…" if len(t.prompt) > 60 else ""),
        )
    console.print(table)
    return 0


def _ago(ts: float) -> str:
    return _human_seconds(int(time.time() - ts)) + " ago"


def _human_seconds(s: int) -> str:
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m"
    if s < 86400:
        return f"{s // 3600}h"
    return f"{s // 86400}d"


async def _run_task(task: Task) -> None:
    """Run a single task by invoking the agent with its prompt."""
    from agents import Runner, SQLiteSession

    from .agent import build_agent
    from .config import SESSION_DB
    from .integrations import build_servers

    servers = build_servers()
    connected = []
    for s in servers:
        try:
            await s.connect()
            connected.append(s)
        except Exception:
            pass

    agent = build_agent(mcp_servers=connected)
    session = SQLiteSession(f"scheduler:{task.name}", str(SESSION_DB))
    try:
        result = await Runner.run(agent, task.prompt, session=session)
        audit.log_tool_call(
            f"scheduler:{task.name}",
            {"prompt": task.prompt},
            result.final_output,
        )
    except Exception as e:
        audit.log_tool_call(f"scheduler:{task.name}", {"prompt": task.prompt}, f"ERROR: {e}")
    finally:
        _mark_ran(task.name)
        for s in connected:
            try:
                await s.cleanup()
            except Exception:
                pass


async def _daemon_loop(interval: int = 30) -> None:
    console.print(f"[bold cyan]jarvis daemon[/] running. tick every {interval}s. Ctrl-C to stop.")
    while True:
        for task in _due():
            console.print(f"[dim]{time.strftime('%H:%M:%S')}[/] running [bold]{task.name}[/]")
            try:
                await _run_task(task)
            except Exception as e:
                console.print(f"[red]task {task.name} failed:[/] {e}")
        await asyncio.sleep(interval)


def daemon(interval: int = 30) -> int:
    try:
        asyncio.run(_daemon_loop(interval))
    except KeyboardInterrupt:
        console.print("\n[dim]daemon stopped.[/]")
    return 0
