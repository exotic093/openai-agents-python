#!/usr/bin/env bash
# One-shot setup for Jarvis.
#
#   curl -fsSL https://raw.githubusercontent.com/exotic093/openai-agents-python/claude/research-ai-assistant-tools-02wqC/jarvis/setup.sh | bash
#
# Or, from a cloned repo:
#
#   cd jarvis && bash setup.sh

set -euo pipefail

cyan() { printf "\033[1;36m%s\033[0m\n" "$*"; }
green() { printf "\033[1;32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[1;33m%s\033[0m\n" "$*"; }
red() { printf "\033[1;31m%s\033[0m\n" "$*"; }

cyan "── jarvis: one-shot setup ──"

# 1. Prereqs
need_node=0
if ! command -v node >/dev/null 2>&1; then
  yellow "node not found — install Node.js ≥20 from https://nodejs.org/"
  need_node=1
fi

if ! command -v uv >/dev/null 2>&1; then
  yellow "uv not found — installing"
  curl -fsSL https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Locate jarvis dir (script lives inside it)
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR"

# 3. Install jarvis (editable, pulls Agents SDK from parent dir)
cyan "installing jarvis"
uv pip install -e . --quiet

# 4. .env
if [[ ! -f .env ]]; then
  cp .env.example .env
  green "created .env from template"
  yellow "edit $SCRIPT_DIR/.env and set OPENAI_API_KEY before continuing"
fi

# 5. Bootstrap (creates dirs, seeds profile, pre-warms MCP packages)
cyan "running bootstrap"
uv run python -m jarvis bootstrap

# 6. Done
green "── setup complete ──"
echo
echo "Next:"
echo "  1. edit .env to set OPENAI_API_KEY (and JARVIS_USER=Sir if not yet)"
echo "  2. uv run python -m jarvis auth all   # walk through integration logins"
echo "  3. uv run python -m jarvis            # start"

if [[ $need_node -eq 1 ]]; then
  yellow "reminder: install Node.js ≥20 to enable npm-based integrations"
fi
