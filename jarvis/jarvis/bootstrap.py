"""`jarvis bootstrap` — one-shot setup that does every non-login step.

Verifies prerequisites, creates data dirs, copies .env.example -> .env if
missing, pre-warms MCP server packages so first launch is fast, and
seeds the user profile. Anything requiring a login is left for `jarvis auth`.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .config import DATA_DIR
from .integrations import REGISTRY

console = Console()

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
ENV_EXAMPLE = Path(__file__).resolve().parent.parent / ".env.example"


def _check(cmd: str) -> str | None:
    return shutil.which(cmd)


def _step(msg: str) -> None:
    console.print(f"[bold cyan]·[/] {msg}")


def _ok(msg: str) -> None:
    console.print(f"  [green]✓[/] {msg}")


def _warn(msg: str) -> None:
    console.print(f"  [yellow]![/] {msg}")


def _fail(msg: str) -> None:
    console.print(f"  [red]✗[/] {msg}")


def check_prereqs() -> bool:
    _step("checking prerequisites")
    ok = True

    node = _check("node")
    if node:
        try:
            v = subprocess.check_output([node, "--version"], text=True).strip()
            _ok(f"node {v}")
        except Exception:
            _ok("node found")
    else:
        _warn("node not found — npm-based MCP servers (gmail, slack, notion, etc.) won't work")
        ok = False

    npx = _check("npx")
    if npx:
        _ok("npx available")
    else:
        _warn("npx not found — install Node.js ≥20 from https://nodejs.org/")

    uvx = _check("uvx")
    if uvx:
        _ok("uvx available")
    else:
        _warn("uvx not found — Python-based MCP (whatsapp, telegram, mt5) won't work. Install: `pip install uv`")

    return ok


def ensure_dirs() -> None:
    _step("creating data directories")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _ok(str(DATA_DIR))


def ensure_env() -> None:
    _step("checking .env")
    if ENV_PATH.exists():
        _ok(f".env exists at {ENV_PATH}")
        return
    if not ENV_EXAMPLE.exists():
        _fail(".env.example missing — reinstall jarvis")
        return
    shutil.copy(ENV_EXAMPLE, ENV_PATH)
    _ok(f"copied .env.example → {ENV_PATH}; edit it to set OPENAI_API_KEY")


def prewarm_packages() -> None:
    """Run each MCP server package once so npx/uvx caches them.

    Failures are logged but non-fatal; the integration just won't be ready
    until the package is actually fetched on first use.
    """
    _step("pre-warming MCP server packages (this may take a while)")
    seen: set[tuple[str, str]] = set()
    for integration in REGISTRY:
        if integration.transport != "stdio":
            continue
        cmd = integration.command
        if not integration.args:
            continue
        # The package name is the last positional after flags.
        pkg = next((a for a in integration.args if not a.startswith("-")), None)
        if not pkg:
            continue
        key = (cmd, pkg)
        if key in seen:
            continue
        seen.add(key)
        if not _check(cmd):
            continue
        # Use --help so the package downloads but exits fast.
        try:
            subprocess.run(
                [cmd, pkg, "--help"] if cmd == "uvx" else [cmd, "-y", pkg, "--help"],
                timeout=120,
                capture_output=True,
                text=True,
                check=False,
            )
            _ok(f"cached {pkg}")
        except subprocess.TimeoutExpired:
            _warn(f"{pkg} timed out — will fetch on first real use")
        except Exception as e:
            _warn(f"{pkg}: {e}")


def seed_profile() -> None:
    _step("seeding profile facts")
    from . import seed_data

    n = seed_data.seed(overwrite=False)
    if n:
        _ok(f"wrote {n} new profile facts to long-term memory")
    else:
        _ok("profile already seeded; nothing to do")


def run(skip_prewarm: bool = False) -> int:
    console.print(
        Panel.fit(
            "[bold cyan]jarvis bootstrap[/] — one-shot setup.\n"
            "Handles every step that doesn't need you to log in somewhere.",
            border_style="cyan",
        )
    )
    check_prereqs()
    ensure_dirs()
    ensure_env()
    seed_profile()
    if not skip_prewarm:
        prewarm_packages()
    console.print(
        Panel.fit(
            "[bold green]bootstrap complete.[/]\n\n"
            f"1. Open [bold]{ENV_PATH}[/] and set [bold]OPENAI_API_KEY[/].\n"
            "2. Run [bold]jarvis auth all[/] (or pick individual integrations).\n"
            "3. Run [bold]jarvis[/] to start chatting.",
            border_style="green",
        )
    )
    return 0
