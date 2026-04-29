"""CLI entry point: `jarvis` (text mode) or `jarvis voice` (voice mode)."""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(prog="jarvis", description="Personal AI assistant.")
    parser.add_argument(
        "mode",
        nargs="?",
        default="text",
        choices=["text", "voice", "onboard"],
        help="text REPL (default), voice mode, or onboarding interview.",
    )
    args = parser.parse_args()

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
