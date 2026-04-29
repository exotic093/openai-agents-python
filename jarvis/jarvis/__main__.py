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
        choices=["text", "voice"],
        help="Interaction mode (default: text).",
    )
    args = parser.parse_args()

    if args.mode == "voice":
        from . import voice

        voice.run()
    else:
        from . import text

        text.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
