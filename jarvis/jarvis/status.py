"""`jarvis status` — single-screen dashboard of everything Jarvis sees."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import audit
from .config import DATA_DIR, MEMORY_DB, SESSION_DB, settings
from .integrations import REGISTRY
from .memory import get_store
from .profile import is_onboarded
from .tools import ALL_TOOLS

console = Console()


def _kv_table(title: str, rows: list[tuple[str, str]]) -> Table:
    table = Table(title=title, show_header=False, box=None, padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    for k, v in rows:
        table.add_row(k, v)
    return table


def run() -> int:
    # Core
    console.print(
        Panel.fit(
            f"[bold cyan]JARVIS[/] · {settings.user_name} · model {settings.text_model}\n"
            f"workspace: {settings.workspace}\n"
            f"data dir:  {DATA_DIR}",
            border_style="cyan",
        )
    )

    # Prereqs
    rows = [
        (
            "node",
            shutil.which("node") or "[red]missing[/]",
        ),
        ("uvx", shutil.which("uvx") or "[red]missing[/]"),
        (
            "OPENAI_API_KEY",
            "[green]set[/]" if os.environ.get("OPENAI_API_KEY") else "[red]missing[/]",
        ),
        ("shell tool", "enabled" if settings.allow_shell else "disabled"),
    ]
    console.print(_kv_table("prerequisites", rows))

    # Memory
    store = get_store()
    all_rows = store.all(limit=10_000)
    memory_size = MEMORY_DB.stat().st_size if Path(MEMORY_DB).exists() else 0
    rows = [
        ("memories", str(len(all_rows))),
        ("memory.db", f"{memory_size / 1024:.1f} KB"),
        (
            "sessions.db",
            f"{SESSION_DB.stat().st_size / 1024:.1f} KB" if Path(SESSION_DB).exists() else "—",
        ),
        ("onboarded", "yes" if is_onboarded() else "[yellow]no — run `jarvis onboard`[/]"),
    ]
    console.print(_kv_table("memory", rows))

    # Tools
    console.print(_kv_table("built-in tools", [(t.name, "") for t in ALL_TOOLS]))

    # Integrations
    table = Table(title="integrations", show_header=True, header_style="bold")
    table.add_column("name")
    table.add_column("status")
    table.add_column("transport")
    for integration in REGISTRY:
        active = integration.is_configured()
        table.add_row(
            integration.name,
            "[green]●[/]" if active else "[dim]○[/]",
            integration.transport,
        )
    console.print(table)

    # Recent audit entries
    recent = audit.tail(5)
    if recent:
        body = "\n".join(f"  {r['tool']:<20} {str(r.get('args'))[:40]}" for r in recent)
        console.print(Panel(body, title="last 5 tool calls", border_style="dim"))

    return 0
