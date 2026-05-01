"""Trading-specific helpers — market clock, position sizing, Monte Carlo."""

from __future__ import annotations

import datetime as _dt
import random
from typing import Literal

from agents import function_tool

# Approximate session windows in UTC. Sufficient for "is the market open?"
# without pulling a calendar service.
_SESSIONS: dict[str, tuple[str, int, int]] = {
    "forex": ("24/5", 0, 24),  # rolls Mon 00:00 UTC → Fri 22:00 UTC
    "nyse": ("us_equities", 14, 21),  # 09:30–16:00 ET ≈ 14:30–21:00 UTC
    "lse": ("uk_equities", 8, 16),
    "tadawul": ("saudi_equities", 7, 12),  # 10:00–15:00 AST
    "dfm": ("uae_equities", 6, 10),  # 10:00–14:00 GST
    "comex_gold": ("metals", 23, 22),  # nearly 24h via CME Globex
    "ice_cocoa": ("softs", 8, 18),
}


@function_tool
def market_status(market: str = "forex") -> str:
    """Report whether a market is currently open.

    Args:
        market: One of forex, nyse, lse, tadawul, dfm, comex_gold, ice_cocoa.
    """
    key = market.lower()
    if key not in _SESSIONS:
        return f"unknown market {market!r}; known: {', '.join(sorted(_SESSIONS))}"
    label, start, end = _SESSIONS[key]
    now = _dt.datetime.now(_dt.timezone.utc)
    weekday = now.weekday()  # 0=Mon
    open_today = weekday < 5  # close on Sat/Sun for most
    if key == "forex":
        # Forex is open Mon 00:00 UTC through Fri 22:00 UTC.
        if weekday == 5 or (weekday == 6 and now.hour < 22):
            return "forex: closed (weekend)."
        return "forex: open (~24/5)."
    if not open_today:
        return f"{key} ({label}): closed (weekend)."
    open_now = start <= now.hour < end
    when = f"{start:02d}:00–{end:02d}:00 UTC"
    return f"{key} ({label}): {'open' if open_now else 'closed'}. session {when}."


@function_tool
def position_size(
    account_balance: float,
    risk_pct: float,
    entry: float,
    stop: float,
    contract_value: float = 1.0,
) -> str:
    """Compute position size for a fixed-fractional risk model.

    Args:
        account_balance: Total account equity, in account currency.
        risk_pct: Percent of equity to risk on the trade (e.g. 1.0 for 1%).
        entry: Planned entry price.
        stop: Planned stop-loss price.
        contract_value: PnL per 1.0 of price move per 1 unit (1.0 for spot).
    """
    if entry == stop:
        return "entry equals stop; no risk distance."
    risk_amount = account_balance * (risk_pct / 100.0)
    distance = abs(entry - stop)
    if distance == 0 or contract_value == 0:
        return "invalid inputs."
    units = risk_amount / (distance * contract_value)
    notional = units * entry * contract_value
    return (
        f"risk_amount={risk_amount:,.2f}  "
        f"distance={distance:.4f}  "
        f"units={units:.4f}  "
        f"notional={notional:,.2f}"
    )


@function_tool
def monte_carlo_path(
    spot: float,
    drift: float,
    volatility: float,
    days: int = 30,
    paths: int = 1000,
    seed: int | None = None,
) -> str:
    """Run a quick GBM Monte Carlo and return summary stats.

    Args:
        spot: Current price.
        drift: Annualized drift (e.g. 0.05 for 5%).
        volatility: Annualized volatility (e.g. 0.20).
        days: Horizon in trading days (252/year).
        paths: Number of sample paths (capped at 50_000).
        seed: Optional RNG seed for reproducibility.
    """
    if seed is not None:
        random.seed(seed)
    paths = min(max(paths, 10), 50_000)
    dt = 1 / 252
    finals: list[float] = []
    for _ in range(paths):
        s = spot
        for _ in range(days):
            z = random.gauss(0.0, 1.0)
            s *= 2.718281828 ** (
                (drift - 0.5 * volatility * volatility) * dt + volatility * (dt**0.5) * z
            )
        finals.append(s)
    finals.sort()
    mean = sum(finals) / len(finals)

    def q(p: float) -> float:
        i = max(0, min(len(finals) - 1, int(p * len(finals))))
        return finals[i]

    return (
        f"paths={paths} horizon={days}d  "
        f"mean={mean:,.4f}  "
        f"p05={q(0.05):,.4f}  p50={q(0.50):,.4f}  p95={q(0.95):,.4f}  "
        f"max={finals[-1]:,.4f}  min={finals[0]:,.4f}"
    )


@function_tool
def risk_reward(
    entry: float,
    stop: float,
    target: float,
    side: Literal["long", "short"] = "long",
) -> str:
    """Compute R:R given entry, stop, and target."""
    if side == "long":
        reward = target - entry
        risk = entry - stop
    else:
        reward = entry - target
        risk = stop - entry
    if risk <= 0:
        return "stop on the wrong side of entry."
    if reward <= 0:
        return "target on the wrong side of entry."
    return f"R:R = 1:{reward / risk:.2f}  (risk={risk:.4f}, reward={reward:.4f})"
