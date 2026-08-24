"""CLI entry point for Jarvis."""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(prog="jarvis", description="Personal AI assistant.")
    parser.add_argument(
        "mode",
        nargs="?",
        default="text",
        choices=[
            "text",
            "voice",
            "onboard",
            "seed",
            "auth",
            "bootstrap",
            "status",
            "brief",
            "schedule",
            "daemon",
        ],
        help="text REPL (default), voice, onboarding, seed, auth, bootstrap, status, brief, schedule, daemon.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help=(
            "For `auth`: integration name. "
            "For `schedule`: subcommand (list/add/remove/enable/disable)."
        ),
    )
    parser.add_argument("args", nargs="*", help="Trailing arguments for subcommands.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="When seeding, overwrite existing facts.",
    )
    parser.add_argument(
        "--skip-prewarm",
        action="store_true",
        help="When bootstrapping, skip the MCP package pre-fetch step.",
    )
    parser.add_argument(
        "--every",
        type=int,
        default=300,
        help="For `schedule add`: interval in seconds (default 300).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="For `daemon`: tick interval in seconds (default 30).",
    )
    parsed = parser.parse_args()

    if parsed.mode == "bootstrap":
        from . import bootstrap

        return bootstrap.run(skip_prewarm=parsed.skip_prewarm)

    if parsed.mode == "auth":
        from . import auth

        return auth.run(parsed.target)

    if parsed.mode == "seed":
        from . import seed_data

        n = seed_data.seed(overwrite=parsed.overwrite)
        print(f"seeded {n} profile facts into long-term memory.")
        return 0

    if parsed.mode == "onboard":
        from . import profile

        profile.run_onboarding()
        return 0

    if parsed.mode == "status":
        from . import status

        return status.run()

    if parsed.mode == "brief":
        from . import brief

        return brief.run()

    if parsed.mode == "schedule":
        from . import scheduler

        sub = parsed.target or "list"
        if sub == "list":
            return scheduler.show()
        if sub == "add":
            if len(parsed.args) < 2:
                print("usage: jarvis schedule add <name> <prompt...> --every <seconds>")
                return 2
            name = parsed.args[0]
            prompt = " ".join(parsed.args[1:])
            print(scheduler.add(name, parsed.every, prompt))
            return 0
        if sub == "remove":
            if not parsed.args:
                print("usage: jarvis schedule remove <name>")
                return 2
            print(scheduler.remove(parsed.args[0]))
            return 0
        if sub in {"enable", "disable"}:
            if not parsed.args:
                print(f"usage: jarvis schedule {sub} <name>")
                return 2
            print(scheduler.toggle(parsed.args[0], enabled=(sub == "enable")))
            return 0
        print(f"unknown schedule subcommand: {sub}")
        return 2

    if parsed.mode == "daemon":
        from . import scheduler

        return scheduler.daemon(interval=parsed.interval)

    # Auto-trigger onboarding on first run so Jarvis actually knows the user.
    from . import profile

    if not profile.is_onboarded():
        profile.run_onboarding()

    if parsed.mode == "voice":
        from . import voice

        voice.run()
    else:
        from . import text

        text.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
