"""`jarvis brief` — generate a morning briefing using the full agent."""

from __future__ import annotations

import asyncio

from agents import Runner, SQLiteSession
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .agent import build_agent
from .config import SESSION_DB
from .integrations import build_servers

console = Console()

BRIEFING_PROMPT = """\
Give me my morning briefing, Sir-style. Keep it concise and useful.

Cover, using whichever tools are available:
1. Date / day of week / Dubai local time.
2. Status of the major markets relevant to my book (forex, gold, silver,
   cocoa) — open, closed, key sessions today.
3. Top emails / Slack DMs / WhatsApp messages I should know about, if those
   integrations are connected (skip silently if not).
4. Calendar: today's events. Skip silently if no calendar integration.
5. Any reminders, todos, or prior memories that look time-relevant today.
6. One sharp suggestion for what to focus on first.

Skip any sections where the relevant tool isn't connected. Don't pad.
"""


async def _run() -> None:
    servers = build_servers()
    connected = []
    for s in servers:
        try:
            await s.connect()
            connected.append(s)
        except Exception as e:
            console.print(f"[yellow]integration {getattr(s, 'name', '?')} skipped: {e}[/]")

    agent = build_agent(mcp_servers=connected)
    session = SQLiteSession("brief", str(SESSION_DB))
    try:
        result = await Runner.run(agent, BRIEFING_PROMPT, session=session)
        console.print(
            Panel(
                Markdown(result.final_output or ""),
                title="morning brief",
                border_style="cyan",
            )
        )
    finally:
        for s in connected:
            try:
                await s.cleanup()
            except Exception:
                pass


def run() -> int:
    asyncio.run(_run())
    return 0
