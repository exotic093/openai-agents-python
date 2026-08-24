"""Interactive text-mode REPL for Jarvis (streaming output)."""

from __future__ import annotations

import asyncio

from agents import Runner, SQLiteSession
from openai.types.responses import ResponseTextDeltaEvent
from rich.console import Console
from rich.panel import Panel

from . import audit
from .agent import build_agent
from .config import SESSION_DB, settings
from .integrations import build_servers, status_report
from .profile import profile_block, run_onboarding

console = Console()


async def _run() -> None:
    servers = build_servers()
    # Connect every MCP server; tolerate failures so a broken integration
    # doesn't take down the whole assistant.
    connected = []
    for s in servers:
        try:
            await s.connect()
            connected.append(s)
        except Exception as e:
            console.print(f"[yellow]integration {getattr(s, 'name', '?')} failed: {e}[/]")

    agent = build_agent(mcp_servers=connected)
    session = SQLiteSession("default", str(SESSION_DB))

    console.print(
        Panel.fit(
            f"[bold cyan]JARVIS[/] online. Model: {settings.text_model}. "
            f"Workspace: {settings.workspace}.\n"
            f"Integrations:\n{status_report()}\n"
            "Commands: [bold]/exit[/] quit · [bold]/reset[/] clear session · "
            "[bold]/profile[/] view · [bold]/onboard[/] re-run interview · "
            "[bold]/integrations[/] status.",
            border_style="cyan",
        )
    )

    try:
        await _repl(agent, session)
    finally:
        for s in connected:
            try:
                await s.cleanup()
            except Exception:
                pass


async def _repl(agent, session) -> None:
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
        if user_input == "/profile":
            console.print(Panel(profile_block(), title="profile", border_style="magenta"))
            continue
        if user_input == "/onboard":
            run_onboarding()
            # Rebuild instructions in place so new profile flows in.
            agent.instructions = build_agent(mcp_servers=agent.mcp_servers).instructions
            continue
        if user_input == "/integrations":
            console.print(Panel(status_report(), title="integrations", border_style="magenta"))
            continue

        try:
            result = Runner.run_streamed(agent, input=user_input, session=session)
            console.print("[bold cyan]jarvis›[/] ", end="")
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(
                    event.data, ResponseTextDeltaEvent
                ):
                    console.print(event.data.delta, end="", soft_wrap=True, highlight=False)
                elif event.type == "run_item_stream_event":
                    item = event.item
                    if item.type == "tool_call_item":
                        raw = getattr(item, "raw_item", None)
                        name = getattr(raw, "name", "tool")
                        args = getattr(raw, "arguments", "")
                        console.print(f"\n[dim]· tool: {name} {args}[/]")
                        audit.log_tool_call(name, {"arguments": args}, "(pending)")
                    elif item.type == "tool_call_output_item":
                        output = getattr(item, "output", "")
                        audit.log_tool_call("(result)", {}, output)
            console.print()  # final newline after stream
        except Exception as e:
            console.print(f"\n[red]error:[/] {e}")
            continue


def run() -> None:
    asyncio.run(_run())
