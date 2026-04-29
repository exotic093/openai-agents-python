# Jarvis

A personal AI assistant built on the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python).
Text + voice modes, persistent long-term memory, file/shell/web tools, and an
agent loop that takes initiative.

## Quick start

```bash
# 1. From the repo root, install Jarvis (uses the local Agents SDK)
cd jarvis
uv pip install -e .

# 2. Configure
cp .env.example .env
# edit .env and set OPENAI_API_KEY

# 3. Run text mode
jarvis

# Or voice mode (needs a working mic + speakers)
jarvis voice
```

## What it can do out of the box

| Tool | Description |
| --- | --- |
| `get_time` | Current time, optional timezone |
| `system_info` | OS / machine / user info |
| `run_shell` | Run a shell command in the workspace |
| `read_file`, `write_file`, `list_dir` | File ops scoped to workspace |
| `web_search`, `fetch_url` | DuckDuckGo search + URL fetch |
| `open_url`, `open_path` | Open in default browser / app |
| `remember`, `recall`, `list_memories`, `forget_memory` | Long-term memory |

Long-term memory persists in `~/.jarvis/memory.db`. The agent is instructed
to write to it whenever you share something worth remembering.

## Onboarding

Two ways to give Jarvis its initial knowledge of you:

**Pre-seeded profile (fastest):**

```bash
jarvis seed              # writes the bundled profile facts; skips ones already present
jarvis seed --overwrite  # force-refresh
```

Edit `jarvis/seed_data.py` to change the bundled facts.

**Interactive interview:**

```bash
jarvis onboard
```

A 25-question briefing covering identity, work, hobbies, lifestyle,
relationships, goals, communication style, and privacy boundaries.

Either way, facts land in `~/.jarvis/memory.db` and are injected into Jarvis's
system prompt every session under `=== USER PROFILE ===`.

View / refresh anytime: `/profile` or `/onboard` inside the REPL.

## REPL commands (text mode)

- `/exit` — quit
- `/reset` — clear conversation session (memory is preserved)
- `/profile` — print everything Jarvis knows about you
- `/onboard` — rerun the interview to add/update facts

## Configuration

All knobs live in `.env` — see `.env.example`. Notable ones:

- `JARVIS_WORKSPACE` — where file ops + shell run.
- `JARVIS_ALLOW_SHELL=0` — disable shell entirely.
- `JARVIS_MODEL`, `JARVIS_VOICE_MODEL`, `JARVIS_VOICE` — model/voice overrides.

## Extending

Drop a new `@function_tool`-decorated function into `jarvis/tools/` and add it
to `ALL_TOOLS` in `jarvis/tools/__init__.py`. To plug in an MCP server (Slack,
Gmail, smart-home, etc.), construct an `MCPServerStdio`/`MCPServerStreamableHttp`
and pass it via `mcp_servers=[...]` on the `Agent` in `jarvis/agent.py`.
