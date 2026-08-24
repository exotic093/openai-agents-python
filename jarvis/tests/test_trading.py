"""Tests for the trading-specific tools."""

from __future__ import annotations

import asyncio
import json


def _call(tool, **kwargs) -> str:
    return asyncio.run(tool.on_invoke_tool(None, json.dumps(kwargs)))


def test_market_status_known() -> None:
    from jarvis.tools.trading import market_status

    out = _call(market_status, market="nyse")
    assert "nyse" in out
    assert "open" in out or "closed" in out


def test_market_status_unknown() -> None:
    from jarvis.tools.trading import market_status

    out = _call(market_status, market="not_a_market")
    assert "unknown" in out


def test_position_size_basic() -> None:
    from jarvis.tools.trading import position_size

    out = _call(
        position_size,
        account_balance=100_000,
        risk_pct=1.0,
        entry=2400.0,
        stop=2380.0,
    )
    # 1% of 100k = $1000, distance 20, units = 50, notional = 120_000
    assert "units=50.0" in out
    assert "notional=120,000" in out


def test_position_size_zero_distance() -> None:
    from jarvis.tools.trading import position_size

    out = _call(position_size, account_balance=1000, risk_pct=1, entry=100, stop=100)
    assert "no risk distance" in out


def test_risk_reward_long() -> None:
    from jarvis.tools.trading import risk_reward

    out = _call(risk_reward, entry=100, stop=95, target=115, side="long")
    # risk 5, reward 15 → 1:3.00
    assert "1:3.00" in out


def test_risk_reward_invalid() -> None:
    from jarvis.tools.trading import risk_reward

    out = _call(risk_reward, entry=100, stop=110, target=115, side="long")
    assert "wrong side" in out


def test_monte_carlo_runs() -> None:
    from jarvis.tools.trading import monte_carlo_path

    out = _call(
        monte_carlo_path,
        spot=100.0,
        drift=0.05,
        volatility=0.2,
        days=10,
        paths=500,
        seed=42,
    )
    assert "p50=" in out
    assert "p95=" in out
    assert "paths=500" in out
