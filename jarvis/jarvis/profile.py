"""Interactive onboarding that builds Jarvis's knowledge of the user."""

from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel

from .memory import get_store

console = Console()


@dataclass(frozen=True)
class ProfileQuestion:
    key: str
    prompt: str
    multi: bool = False  # accept comma-separated list


PROFILE_QUESTIONS: list[ProfileQuestion] = [
    ProfileQuestion("identity.name", "What's your full name?"),
    ProfileQuestion("identity.preferred_name", "What should I call you?"),
    ProfileQuestion("identity.pronouns", "Pronouns? (skip if you'd rather not say)"),
    ProfileQuestion("identity.birthday", "Birthday (YYYY-MM-DD or 'skip')?"),
    ProfileQuestion("identity.location", "Where are you based (city, country)?"),
    ProfileQuestion("identity.timezone", "Timezone (e.g. America/New_York)?"),
    ProfileQuestion("identity.languages", "Languages you speak?", multi=True),
    ProfileQuestion("work.role", "What do you do for work — title and company?"),
    ProfileQuestion("work.focus", "What are you currently focused on at work?"),
    ProfileQuestion("work.tools", "Main tools/stack you use day to day?", multi=True),
    ProfileQuestion("work.schedule", "Typical work hours / schedule?"),
    ProfileQuestion("hobbies.interests", "Hobbies and interests?", multi=True),
    ProfileQuestion("hobbies.media", "Favorite movies, shows, books, or games?", multi=True),
    ProfileQuestion("hobbies.music", "Music taste — genres or artists?", multi=True),
    ProfileQuestion("lifestyle.diet", "Dietary preferences or restrictions?"),
    ProfileQuestion("lifestyle.fitness", "Fitness routine or sports?"),
    ProfileQuestion("lifestyle.sleep", "Typical sleep schedule?"),
    ProfileQuestion("relationships.family", "Important people in your life I should know about?"),
    ProfileQuestion("relationships.pets", "Any pets?"),
    ProfileQuestion("goals.short_term", "Main goals for the next few months?", multi=True),
    ProfileQuestion("goals.long_term", "Bigger long-term goals?", multi=True),
    ProfileQuestion(
        "preferences.communication", "How should I talk to you — formal, casual, blunt, witty?"
    ),
    ProfileQuestion("preferences.units", "Metric or imperial? 24h or 12h time?"),
    ProfileQuestion("preferences.privacy", "Anything I should NEVER bring up or store?"),
    ProfileQuestion("preferences.misc", "Anything else important about you I should remember?"),
]


def is_onboarded() -> bool:
    return bool(get_store().recall("identity.preferred_name", limit=1))


def run_onboarding() -> None:
    store = get_store()
    console.print(
        Panel.fit(
            "[bold cyan]JARVIS — initial briefing[/]\n"
            "I'm going to ask a few questions so I actually know you.\n"
            "Hit enter to skip any question. Type [bold]/quit[/] to bail out.",
            border_style="cyan",
        )
    )
    saved = 0
    for q in PROFILE_QUESTIONS:
        try:
            answer = console.input(f"[bold green]?[/] {q.prompt}\n  ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]onboarding interrupted; what was given is saved.[/]")
            break
        if not answer or answer.lower() in {"skip", "-", "n/a"}:
            continue
        if answer == "/quit":
            break
        store.remember(q.key, answer)
        saved += 1
    console.print(f"[green]saved {saved} facts to long-term memory.[/]")
    console.print(
        '[dim]you can update anytime — just tell me, e.g. "remember that I switched jobs to X".[/]'
    )


def profile_block(limit: int = 100) -> str:
    """Format all profile.* memories for the agent's system prompt."""
    rows = get_store().all(limit=limit)
    profile_rows = [m for m in rows if "." in m.key]
    if not profile_rows:
        return "(no profile yet — ask the user to run `jarvis onboard`)"
    by_section: dict[str, list[str]] = {}
    for m in profile_rows:
        section = m.key.split(".", 1)[0]
        by_section.setdefault(section, []).append(f"  - {m.key.split('.', 1)[1]}: {m.value}")
    parts = []
    for section, items in by_section.items():
        parts.append(f"[{section}]\n" + "\n".join(items))
    return "\n".join(parts)
