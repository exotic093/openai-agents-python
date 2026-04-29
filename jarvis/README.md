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

## Integrations (MCP)

Jarvis ships with a registry of MCP integrations covering the most common
productivity, comms, and trading surfaces. Each is enabled automatically when
its credentials are present in `.env`; nothing else is required.

| Integration | Env vars | What it grants |
| --- | --- | --- |
| Gmail | `GMAIL_OAUTH_PATH` | Read, search, draft, label, send mail |
| Outlook / M365 | `MS365_CLIENT_ID`, `MS365_TENANT_ID` | Mail, calendar, contacts, files |
| Google Calendar | `GCAL_OAUTH_PATH` | List/create/update events, free-busy |
| Calendly | `CALENDLY_API_TOKEN`, `CALENDLY_MCP_URL` | Event types, scheduling links, invitees |
| Slack | `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID` | Read channels/threads/DMs, send messages |
| WhatsApp | `WHATSAPP_SESSION_PATH` | Read chats, search, send |
| Telegram | `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` | Read chats, search, send |
| Notion | `NOTION_API_TOKEN` | Search/read/create/update pages and DBs |
| TradingView | `TRADINGVIEW_USERNAME`, `TRADINGVIEW_PASSWORD` | Quotes, indicators, alerts |
| MetaTrader 5 | `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER` | Account, positions, market data, trade execution |
| Broker (HTTP) | `BROKER_MCP_URL`, `BROKER_MCP_TOKEN` | Generic broker MCP (Alpaca, IB, etc.) |
| HubSpot CRM | `HUBSPOT_ACCESS_TOKEN` | Contacts, companies, deals, notes |
| QuickBooks | `QUICKBOOKS_CLIENT_ID`, `QUICKBOOKS_CLIENT_SECRET`, `QUICKBOOKS_REALM_ID` | Invoices, customers, P&L |

See `.env.example` for the full credential list and links to each MCP
server's documentation. Use `/integrations` in the REPL to see active vs.
inactive integrations.

### Guided setup: `jarvis auth`

```bash
jarvis auth                # list every integration, ● = configured / ○ = not
jarvis auth gmail          # walk through Gmail credentials
jarvis auth slack          # walk through Slack bot setup
jarvis auth mt5            # MetaTrader 5 (alias of metatrader5)
```

Each helper prints what to do, opens the relevant signup/console page in
your browser, prompts for the values (secrets are read with `getpass`), and
writes them to `.env` — preserving existing keys and only rewriting the
ones you change.

> ⚠️ Most npm-distributed MCP servers require `node` ≥ 20 on your `PATH`.
> Auth-scope choices live in each provider's setup docs (link in
> `jarvis/integrations.py`).

## Extending

Drop a new `@function_tool`-decorated function into `jarvis/tools/` and add it
to `ALL_TOOLS` in `jarvis/tools/__init__.py`. To register a new MCP integration,
add an `Integration(...)` entry to `REGISTRY` in `jarvis/integrations.py`.
