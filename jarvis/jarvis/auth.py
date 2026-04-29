"""`jarvis auth` — guided credential setup.

For each integration, prints what to do, opens the right page in the browser,
prompts for the values, and writes them into `.env` (creating it if needed).
Existing keys are preserved; updated keys are rewritten in place.
"""

from __future__ import annotations

import getpass
import re
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


@dataclass
class Field:
    env_var: str
    prompt: str
    secret: bool = False
    default: str = ""
    optional: bool = False


@dataclass
class Provider:
    name: str
    summary: str
    instructions: str
    fields: list[Field]
    url: str | None = None
    aliases: list[str] = field(default_factory=list)


PROVIDERS: list[Provider] = [
    Provider(
        name="gmail",
        summary="Gmail (read/search/draft/label/send)",
        url="https://console.cloud.google.com/apis/credentials",
        instructions=(
            "1. In Google Cloud Console, create OAuth 2.0 client credentials "
            "of type 'Desktop app'.\n"
            "2. Download the client_secret JSON.\n"
            "3. Provide its path below — the MCP server completes the OAuth "
            "dance on first launch and writes the token to OAUTH path.\n"
            "4. Make sure the Gmail API is enabled on the project."
        ),
        fields=[
            Field("GMAIL_CREDENTIALS_PATH", "Path to client_secret.json"),
            Field(
                "GMAIL_OAUTH_PATH",
                "Where to store the OAuth token",
                default=str(Path.home() / ".jarvis/gmail_token.json"),
            ),
        ],
    ),
    Provider(
        name="google_calendar",
        aliases=["gcal", "calendar"],
        summary="Google Calendar (events, free-busy)",
        url="https://console.cloud.google.com/apis/credentials",
        instructions=(
            "Same OAuth client JSON as Gmail can be reused — just enable the "
            "Google Calendar API on the same project, and pass the same "
            "client_secret.json path here."
        ),
        fields=[
            Field("GCAL_CREDENTIALS_PATH", "Path to client_secret.json"),
            Field(
                "GCAL_OAUTH_PATH",
                "Where to store the OAuth token",
                default=str(Path.home() / ".jarvis/gcal_token.json"),
            ),
        ],
    ),
    Provider(
        name="outlook",
        aliases=["m365", "microsoft365"],
        summary="Microsoft 365 / Outlook (mail, calendar, contacts)",
        url="https://entra.microsoft.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade",
        instructions=(
            "1. In Entra ID → App registrations, register a new app.\n"
            "2. Add Microsoft Graph delegated permissions: Mail.ReadWrite, "
            "Mail.Send, Calendars.ReadWrite, Contacts.Read.\n"
            "3. Grant admin consent.\n"
            "4. Copy the Application (client) ID and Directory (tenant) ID.\n"
            "5. (Optional) Create a client secret if you need confidential flow."
        ),
        fields=[
            Field("MS365_CLIENT_ID", "Application (client) ID"),
            Field("MS365_TENANT_ID", "Directory (tenant) ID"),
            Field("MS365_CLIENT_SECRET", "Client secret", secret=True, optional=True),
        ],
    ),
    Provider(
        name="calendly",
        summary="Calendly (scheduling links, invitees)",
        url="https://calendly.com/integrations/api_webhooks",
        instructions=(
            "Generate a Personal Access Token from Integrations → API & "
            "Webhooks. If you self-host the Calendly MCP server, set its URL "
            "below; otherwise use the default."
        ),
        fields=[
            Field("CALENDLY_API_TOKEN", "Personal access token", secret=True),
            Field(
                "CALENDLY_MCP_URL",
                "Calendly MCP server URL",
                default="https://mcp.calendly.com/",
            ),
        ],
    ),
    Provider(
        name="slack",
        summary="Slack (channels, threads, DMs, send)",
        url="https://api.slack.com/apps",
        instructions=(
            "1. Create a Slack app → 'From scratch'.\n"
            "2. OAuth & Permissions → add bot scopes: channels:history, "
            "channels:read, chat:write, groups:history, groups:read, "
            "im:history, im:read, mpim:history, mpim:read, users:read, "
            "search:read.\n"
            "3. Install the app to your workspace, copy the Bot User OAuth "
            "Token (starts with xoxb-).\n"
            "4. Find your Team ID: workspace → About this workspace, or use "
            "the URL slug."
        ),
        fields=[
            Field("SLACK_BOT_TOKEN", "Bot token (xoxb-...)", secret=True),
            Field("SLACK_TEAM_ID", "Team ID (T...)"),
            Field(
                "SLACK_CHANNEL_IDS",
                "Comma-separated channel IDs to expose (optional)",
                optional=True,
            ),
        ],
    ),
    Provider(
        name="whatsapp",
        summary="WhatsApp (read chats, send)",
        url=None,
        instructions=(
            "WhatsApp Web pairs by QR code. Pick a folder where the session "
            "will be persisted; on first launch the MCP server prints a QR "
            "code, which you scan from your phone (Settings → Linked Devices "
            "→ Link a Device)."
        ),
        fields=[
            Field(
                "WHATSAPP_SESSION_PATH",
                "Session storage directory",
                default=str(Path.home() / ".jarvis/whatsapp"),
            ),
        ],
    ),
    Provider(
        name="telegram",
        summary="Telegram (read chats, send)",
        url="https://my.telegram.org/auth",
        instructions=(
            "1. Log in at my.telegram.org with your phone number.\n"
            "2. Go to 'API development tools' and create an application to "
            "get api_id and api_hash.\n"
            "3. The first run of Telegram MCP will ask for your phone and a "
            "login code — that produces the session file."
        ),
        fields=[
            Field("TELEGRAM_API_ID", "api_id"),
            Field("TELEGRAM_API_HASH", "api_hash", secret=True),
            Field(
                "TELEGRAM_SESSION_PATH",
                "Session file path",
                default=str(Path.home() / ".jarvis/telegram.session"),
            ),
        ],
    ),
    Provider(
        name="notion",
        summary="Notion (search/read/create/update pages and DBs)",
        url="https://www.notion.so/my-integrations",
        instructions=(
            "1. Create a new internal integration.\n"
            "2. Copy the Internal Integration Token.\n"
            "3. In every Notion page or database you want Jarvis to access, "
            "click ⋯ → Add connections → select your integration."
        ),
        fields=[
            Field("NOTION_API_TOKEN", "Internal integration token", secret=True),
        ],
    ),
    Provider(
        name="tradingview",
        summary="TradingView (quotes, indicators, alerts)",
        url=None,
        instructions=(
            "The unofficial TradingView bridge logs in with username + "
            "password. Strongly recommend creating a dedicated sub-account "
            "for this rather than reusing your main login."
        ),
        fields=[
            Field("TRADINGVIEW_USERNAME", "Username"),
            Field("TRADINGVIEW_PASSWORD", "Password", secret=True),
        ],
    ),
    Provider(
        name="metatrader5",
        aliases=["mt5"],
        summary="MetaTrader 5 (positions, market data, trade execution)",
        url=None,
        instructions=(
            "Enter your MT5 account login, password, and broker server name "
            "exactly as MT5 displays them. MT5 must be installed; provide "
            "MT5_PATH only if it's in a non-default location."
        ),
        fields=[
            Field("MT5_LOGIN", "Account login number"),
            Field("MT5_PASSWORD", "Account password", secret=True),
            Field("MT5_SERVER", "Broker server (e.g. ICMarketsSC-Live)"),
            Field("MT5_PATH", "Path to terminal64.exe", optional=True),
        ],
    ),
    Provider(
        name="broker_http",
        aliases=["broker"],
        summary="Generic broker MCP over HTTP (Alpaca, IB, etc.)",
        url=None,
        instructions=(
            "If your broker provides an MCP server reachable over HTTP, "
            "supply the URL and bearer token here."
        ),
        fields=[
            Field("BROKER_MCP_URL", "MCP server URL"),
            Field("BROKER_MCP_TOKEN", "Bearer token", secret=True),
        ],
    ),
    Provider(
        name="hubspot",
        summary="HubSpot CRM (contacts, companies, deals)",
        url="https://app.hubspot.com/private-apps",
        instructions=(
            "1. Create a private app in your HubSpot account.\n"
            "2. Grant scopes for the objects you want Jarvis to touch "
            "(crm.objects.contacts, crm.objects.companies, "
            "crm.objects.deals, etc.).\n"
            "3. Copy the access token."
        ),
        fields=[
            Field("HUBSPOT_ACCESS_TOKEN", "Private app access token", secret=True),
        ],
    ),
    Provider(
        name="quickbooks",
        aliases=["qbo"],
        summary="QuickBooks Online (invoices, customers, P&L)",
        url="https://developer.intuit.com/app/developer/myapps",
        instructions=(
            "1. Create an app at developer.intuit.com.\n"
            "2. Connect it to your QuickBooks company; capture the realm "
            "(company) ID.\n"
            "3. Use the OAuth 2.0 Playground (or your own callback) to "
            "obtain a refresh token.\n"
            "4. Paste client id, secret, refresh token, and realm id."
        ),
        fields=[
            Field("QUICKBOOKS_CLIENT_ID", "App client ID"),
            Field("QUICKBOOKS_CLIENT_SECRET", "Client secret", secret=True),
            Field("QUICKBOOKS_REFRESH_TOKEN", "Refresh token", secret=True),
            Field("QUICKBOOKS_REALM_ID", "Realm / company ID"),
        ],
    ),
]


def _find(name: str) -> Provider | None:
    name = name.lower().strip()
    for p in PROVIDERS:
        if p.name == name or name in p.aliases:
            return p
    return None


def _read_env() -> dict[str, str]:
    if not ENV_PATH.exists():
        return {}
    out: dict[str, str] = {}
    for line in ENV_PATH.read_text().splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip()
    return out


def _write_env(values: dict[str, str]) -> None:
    """Merge `values` into `.env`, preserving comments and order of existing keys."""
    if ENV_PATH.exists():
        original = ENV_PATH.read_text().splitlines()
    else:
        original = ["# Jarvis environment", ""]

    seen: set[str] = set()
    out: list[str] = []
    for line in original:
        m = re.match(r"^\s*([A-Z0-9_]+)\s*=", line)
        if m and m.group(1) in values:
            key = m.group(1)
            out.append(f"{key}={values[key]}")
            seen.add(key)
        else:
            out.append(line)

    appended = [k for k in values if k not in seen]
    if appended:
        if out and out[-1] != "":
            out.append("")
        out.append("# Added by `jarvis auth`")
        for k in appended:
            out.append(f"{k}={values[k]}")

    ENV_PATH.write_text("\n".join(out) + "\n")


def _ask(field: Field, current: str | None) -> str | None:
    label = f"{field.env_var}"
    hint = f" [current: ***]" if current and field.secret else (
        f" [current: {current}]" if current else ""
    )
    default = current or field.default
    suffix = f" (default: {default})" if default and not field.secret else ""
    if field.optional:
        suffix += " (optional, blank to skip)"
    console.print(f"[bold]{label}[/]{hint}: {field.prompt}{suffix}")
    if field.secret:
        value = getpass.getpass("  > ")
    else:
        value = input("  > ").strip()
    if not value:
        if default:
            return default
        if field.optional:
            return None
        return current  # keep existing
    return value


def configure(provider: Provider) -> None:
    console.print(
        Panel.fit(
            f"[bold cyan]{provider.name}[/] — {provider.summary}\n\n"
            f"{provider.instructions}",
            border_style="cyan",
        )
    )
    if provider.url:
        try:
            opened = webbrowser.open(provider.url, new=2)
        except Exception:
            opened = False
        if opened:
            console.print(f"[dim]opened {provider.url}[/]")
        else:
            console.print(f"[dim]reference: {provider.url}[/]")

    existing = _read_env()
    new_values: dict[str, str] = {}
    for field in provider.fields:
        result = _ask(field, existing.get(field.env_var))
        if result:
            new_values[field.env_var] = result

    if not new_values:
        console.print("[yellow]nothing entered; .env unchanged.[/]")
        return

    _write_env(new_values)
    console.print(
        f"[green]✓ wrote {len(new_values)} value(s) to {ENV_PATH}.[/] "
        f"Restart Jarvis to pick them up."
    )


def list_providers() -> None:
    env = _read_env()
    rows = []
    for p in PROVIDERS:
        configured = all(env.get(f.env_var) for f in p.fields if not f.optional)
        mark = "[green]●[/]" if configured else "[dim]○[/]"
        rows.append(f"  {mark} [bold]{p.name:<18}[/] {p.summary}")
    console.print(
        Panel("\n".join(rows), title="integrations", border_style="cyan")
    )


def run(name: str | None) -> int:
    if not name:
        list_providers()
        console.print(
            "\nRun [bold]jarvis auth <name>[/] to configure one. "
            "Aliases: gcal, m365, mt5, qbo, broker."
        )
        return 0
    provider = _find(name)
    if provider is None:
        console.print(f"[red]unknown integration: {name}[/]")
        list_providers()
        return 1
    configure(provider)
    return 0
