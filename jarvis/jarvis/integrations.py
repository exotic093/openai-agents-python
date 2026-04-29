"""MCP integrations registry for Jarvis.

Each integration is a data-driven entry that maps to an MCP server. At
startup, `build_servers()` enables only those whose credentials are present
in the environment, so Jarvis runs fine before everything is wired up.

References for the community/official MCP packages used here:
- Gmail / Google Calendar / Drive: https://github.com/GongRzhe/Gmail-MCP-Server
- Microsoft 365 (Outlook): https://github.com/softeria/ms-365-mcp-server
- Calendly: https://github.com/calendly/mcp-server-calendly
- Slack: https://github.com/modelcontextprotocol/servers/tree/main/src/slack
- WhatsApp: https://github.com/lharries/whatsapp-mcp
- Telegram: https://github.com/chigwell/telegram-mcp
- Notion: https://github.com/makenotion/notion-mcp-server
- HubSpot CRM: https://github.com/hubspot/hubspot-mcp-server
- QuickBooks: https://github.com/intuit/quickbooks-mcp
- TradingView: https://github.com/Mathieu2301/TradingView-API (custom MCP wrapper)
- MetaTrader 5: https://github.com/ariadng/metatrader-mcp-server
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal

from agents.mcp import MCPServer, MCPServerStdio, MCPServerStreamableHttp

Transport = Literal["stdio", "http"]


@dataclass
class Integration:
    name: str
    description: str
    transport: Transport
    # Required env vars — integration is skipped if any are missing.
    required_env: list[str] = field(default_factory=list)
    # stdio-only:
    command: str = ""
    args: list[str] = field(default_factory=list)
    env_passthrough: list[str] = field(default_factory=list)
    # http-only:
    url_env: str = ""
    auth_header_env: str = ""
    auth_header_format: str = "Bearer {token}"

    def is_configured(self) -> bool:
        return all(os.environ.get(v) for v in self.required_env)

    def build(self) -> MCPServer | None:
        if not self.is_configured():
            return None
        if self.transport == "stdio":
            return MCPServerStdio(
                params={
                    "command": self.command,
                    "args": self.args,
                    "env": {k: os.environ[k] for k in self.env_passthrough if os.environ.get(k)},
                },
                name=self.name,
                cache_tools_list=True,
            )
        url = os.environ[self.url_env]
        headers: dict[str, str] = {}
        if self.auth_header_env:
            token = os.environ.get(self.auth_header_env, "")
            if token:
                headers["Authorization"] = self.auth_header_format.format(token=token)
        return MCPServerStreamableHttp(
            params={"url": url, "headers": headers},
            name=self.name,
            cache_tools_list=True,
        )


REGISTRY: list[Integration] = [
    # === Email ===
    Integration(
        name="gmail",
        description="Gmail: read, search, draft, label, send (on command).",
        transport="stdio",
        required_env=["GMAIL_OAUTH_PATH"],
        command="npx",
        args=["-y", "@gongrzhe/server-gmail-autoauth-mcp"],
        env_passthrough=["GMAIL_OAUTH_PATH", "GMAIL_CREDENTIALS_PATH"],
    ),
    Integration(
        name="outlook",
        description="Microsoft 365 / Outlook: mail, calendar, contacts, files.",
        transport="stdio",
        required_env=["MS365_CLIENT_ID", "MS365_TENANT_ID"],
        command="npx",
        args=["-y", "@softeria/ms-365-mcp-server"],
        env_passthrough=["MS365_CLIENT_ID", "MS365_TENANT_ID", "MS365_CLIENT_SECRET"],
    ),
    # === Calendars ===
    Integration(
        name="google_calendar",
        description="Google Calendar: list/create/update events, find free time.",
        transport="stdio",
        required_env=["GCAL_OAUTH_PATH"],
        command="npx",
        args=["-y", "@cocal/google-calendar-mcp"],
        env_passthrough=["GCAL_OAUTH_PATH", "GCAL_CREDENTIALS_PATH"],
    ),
    Integration(
        name="calendly",
        description="Calendly: scheduling links, event types, invitees, no-shows.",
        transport="http",
        required_env=["CALENDLY_API_TOKEN", "CALENDLY_MCP_URL"],
        url_env="CALENDLY_MCP_URL",
        auth_header_env="CALENDLY_API_TOKEN",
    ),
    # === Messaging ===
    Integration(
        name="slack",
        description="Slack: read channels/threads/DMs, search, send messages.",
        transport="stdio",
        required_env=["SLACK_BOT_TOKEN", "SLACK_TEAM_ID"],
        command="npx",
        args=["-y", "@modelcontextprotocol/server-slack"],
        env_passthrough=["SLACK_BOT_TOKEN", "SLACK_TEAM_ID", "SLACK_CHANNEL_IDS"],
    ),
    Integration(
        name="whatsapp",
        description="WhatsApp: read chats, search messages, send (on command).",
        transport="stdio",
        required_env=["WHATSAPP_SESSION_PATH"],
        command="npx",
        args=["-y", "@lharries/whatsapp-mcp"],
        env_passthrough=["WHATSAPP_SESSION_PATH"],
    ),
    Integration(
        name="telegram",
        description="Telegram: read chats, search history, send messages.",
        transport="stdio",
        required_env=["TELEGRAM_API_ID", "TELEGRAM_API_HASH"],
        command="npx",
        args=["-y", "@chigwell/telegram-mcp"],
        env_passthrough=[
            "TELEGRAM_API_ID",
            "TELEGRAM_API_HASH",
            "TELEGRAM_SESSION_PATH",
        ],
    ),
    # === Knowledge ===
    Integration(
        name="notion",
        description="Notion: search, read, create, and update pages and databases.",
        transport="stdio",
        required_env=["NOTION_API_TOKEN"],
        command="npx",
        args=["-y", "@notionhq/notion-mcp-server"],
        env_passthrough=["NOTION_API_TOKEN"],
    ),
    # === Trading ===
    Integration(
        name="tradingview",
        description="TradingView: live quotes, indicators, chart screenshots, alerts.",
        transport="stdio",
        required_env=["TRADINGVIEW_USERNAME", "TRADINGVIEW_PASSWORD"],
        command="npx",
        args=["-y", "tradingview-mcp"],
        env_passthrough=["TRADINGVIEW_USERNAME", "TRADINGVIEW_PASSWORD"],
    ),
    Integration(
        name="metatrader5",
        description="MetaTrader 5: account info, positions, orders, market data, trade execution.",
        transport="stdio",
        required_env=["MT5_LOGIN", "MT5_PASSWORD", "MT5_SERVER"],
        command="npx",
        args=["-y", "@ariadng/metatrader-mcp-server"],
        env_passthrough=["MT5_LOGIN", "MT5_PASSWORD", "MT5_SERVER", "MT5_PATH"],
    ),
    Integration(
        name="broker_http",
        description="Generic broker MCP over HTTP (Interactive Brokers, Alpaca, etc.).",
        transport="http",
        required_env=["BROKER_MCP_URL", "BROKER_MCP_TOKEN"],
        url_env="BROKER_MCP_URL",
        auth_header_env="BROKER_MCP_TOKEN",
    ),
    # === CRM / accounting ===
    Integration(
        name="hubspot",
        description="HubSpot CRM: contacts, companies, deals, notes, tasks.",
        transport="stdio",
        required_env=["HUBSPOT_ACCESS_TOKEN"],
        command="npx",
        args=["-y", "@hubspot/mcp-server"],
        env_passthrough=["HUBSPOT_ACCESS_TOKEN"],
    ),
    Integration(
        name="quickbooks",
        description="QuickBooks Online: invoices, customers, expenses, P&L.",
        transport="stdio",
        required_env=["QUICKBOOKS_CLIENT_ID", "QUICKBOOKS_CLIENT_SECRET", "QUICKBOOKS_REALM_ID"],
        command="npx",
        args=["-y", "quickbooks-mcp"],
        env_passthrough=[
            "QUICKBOOKS_CLIENT_ID",
            "QUICKBOOKS_CLIENT_SECRET",
            "QUICKBOOKS_REFRESH_TOKEN",
            "QUICKBOOKS_REALM_ID",
        ],
    ),
]


def build_servers() -> list[MCPServer]:
    """Instantiate every integration whose env vars are present."""
    servers: list[MCPServer] = []
    for integration in REGISTRY:
        srv = integration.build()
        if srv is not None:
            servers.append(srv)
    return servers


def status_report() -> str:
    """Human-readable summary of which integrations are active vs. skipped."""
    on, off = [], []
    for i in REGISTRY:
        (on if i.is_configured() else off).append(i.name)
    lines = []
    if on:
        lines.append("active: " + ", ".join(on))
    if off:
        lines.append("inactive (missing env): " + ", ".join(off))
    return "\n".join(lines) or "(no integrations registered)"
