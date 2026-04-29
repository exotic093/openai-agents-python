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
        choices=["text", "voice", "onboard", "seed", "auth"],
        help="text REPL (default), voice mode, onboarding, profile seed, or integration auth.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="For `auth`: integration name (e.g. gmail, slack). Omit to list.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="When seeding, overwrite existing facts.",
    )
    args = parser.parse_args()

    if args.mode == "auth":
        from . import auth

        return auth.run(args.target)

    if args.mode == "seed":
        from . import seed_data

        n = seed_data.seed(overwrite=args.overwrite)
        print(f"seeded {n} profile facts into long-term memory.")
        return 0

    if args.mode == "onboard":
        from . import profile

        profile.run_onboarding()
        return 0

    # Auto-trigger onboarding on first run so Jarvis actually knows the user.
    from . import profile

    if not profile.is_onboarded():
        profile.run_onboarding()

    if args.mode == "voice":
        from . import voice

        voice.run()
    else:
        from . import text

        text.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
