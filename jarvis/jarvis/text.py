"""Interactive text-mode REPL for Jarvis."""

from __future__ import annotations

import asyncio

from agents import Runner, SQLiteSession
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .agent import build_agent
from .config import SESSION_DB, settings

console = Console()


async def _run() -> None:
    agent = build_agent()
    session = SQLiteSession("default", str(SESSION_DB))

    console.print(
        Panel.fit(
            f"[bold cyan]JARVIS[/] online. Model: {settings.text_model}. "
            f"Workspace: {settings.workspace}.\n"
            "Type your request, or [bold]/exit[/] to quit, [bold]/reset[/] to clear session.",
            border_style="cyan",
        )
    )

    while True:
        try:
            user_input = console.input("[bold green]you›[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]goodbye.[/]")
            return
        if not user_input:
            continue
        if user_input in {"/exit", "/quit"}:
            console.print("[dim]goodbye.[/]")
            return
        if user_input == "/reset":
            await session.clear_session()
            console.print("[yellow]session cleared.[/]")
            continue

        try:
            result = await Runner.run(agent, user_input, session=session)
        except Exception as e:
            console.print(f"[red]error:[/] {e}")
            continue

        console.print(Panel(Markdown(result.final_output or ""), title="jarvis", border_style="cyan"))


def run() -> None:
    asyncio.run(_run())
