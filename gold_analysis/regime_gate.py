"""XAUUSD regime gate, computed as gold-scalp-engine/SKILL.md lines 28-32 and 89-95 define it.

vol ratio = ATR14(H1, Wilder) / median of that ATR over the last 480 completed H1 bars.
daily z   = (last completed D1 close - SMA50 of D1 closes) / ATR14(D1, Wilder), D1 rolling at
            17:00 New York.
The gate is open only when 1.25 <= vol ratio < 2.0 and |daily z| >= 1. It can only block a plan;
it never creates or changes one.

Input is H1 candles (the source names the OANDA:XAUUSD H1 chart). D1 candles are built from them so
that the 17:00 New York roll is always right. Only completed candles are used.

Command line:
    python -m gold_analysis.regime_gate h1.csv [--now 2026-10-08T15:15:00+04:00]
The CSV needs the columns time, high, low and close. ``time`` is the bar's open time, as ISO 8601
with a UTC offset or as Unix seconds.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from statistics import median
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")
H1 = timedelta(hours=1)
DAILY_ROLL = time(17, 0)
ATR_PERIOD = 14
VOL_LOOKBACK = 480
SMA_PERIOD = 50
VOL_OPEN = 1.25
VOL_SHOCK = 2.0
Z_MIN = 1.0


@dataclass(frozen=True)
class Bar:
    """One candle. ``start`` is the timezone-aware open time of the candle."""

    start: datetime
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class RegimeGate:
    """A regime-gate reading and the numbers behind it."""

    as_of: datetime
    gate_open: bool
    reasons: tuple[str, ...]
    volatility_state: str
    vol_ratio: float
    hourly_atr: float
    hourly_atr_median: float
    open_hourly_atr_low: float
    open_hourly_atr_high: float
    daily_z: float
    daily_close: float
    daily_sma50: float
    daily_atr: float
    last_completed_session: date
    h1_bars_used: int
    d1_sessions_used: int


def wilder_atr(bars: Sequence[Bar], period: int = ATR_PERIOD) -> list[float]:
    """Return Wilder's ATR for every bar from index ``period - 1`` onward.

    True range uses the previous close; the first bar's true range is its high-low range. The first
    ATR is the mean of the first ``period`` true ranges, then ATR = (prior ATR * (period - 1) + true
    range) / period.
    """
    if len(bars) < period:
        raise ValueError(f"need at least {period} bars for ATR{period}, got {len(bars)}")
    true_ranges = [bars[0].high - bars[0].low]
    for i in range(1, len(bars)):
        prev_close, bar = bars[i - 1].close, bars[i]
        true_ranges.append(
            max(bar.high - bar.low, abs(bar.high - prev_close), abs(bar.low - prev_close))
        )
    atr = sum(true_ranges[:period]) / period
    values = [atr]
    for true_range in true_ranges[period:]:
        atr = (atr * (period - 1) + true_range) / period
        values.append(atr)
    return values


def session_date(bar_start: datetime) -> date:
    """Return the trading session a candle belongs to; D1 rolls at 17:00 New York time."""
    local = bar_start.astimezone(NEW_YORK)
    if local.time() >= DAILY_ROLL:
        return local.date() + timedelta(days=1)
    return local.date()


def session_close(day: date) -> datetime:
    """Return the close of a trading session: 17:00 New York time on that date."""
    return datetime.combine(day, DAILY_ROLL, tzinfo=NEW_YORK)


def daily_bars(h1_bars: Sequence[Bar], as_of: datetime) -> list[Bar]:
    """Build D1 candles from H1 candles and keep only sessions that closed by ``as_of``."""
    sessions: dict[date, list[Bar]] = {}
    for bar in h1_bars:
        sessions.setdefault(session_date(bar.start), []).append(bar)
    result = []
    for day in sorted(sessions):
        if session_close(day) > as_of:
            continue
        group = sessions[day]
        result.append(
            Bar(
                start=group[0].start,
                high=max(bar.high for bar in group),
                low=min(bar.low for bar in group),
                close=group[-1].close,
            )
        )
    return result


def classify(vol_ratio: float, daily_z: float) -> tuple[bool, str, tuple[str, ...]]:
    """Return (gate open, volatility state, reasons the gate is closed)."""
    if vol_ratio < VOL_OPEN:
        state = "quiet"
    elif vol_ratio < VOL_SHOCK:
        state = "active"
    else:
        state = "shock"
    reasons = []
    if state == "quiet":
        reasons.append(f"quiet volatility: vol ratio below {VOL_OPEN}")
    if state == "shock":
        reasons.append(f"shock volatility: vol ratio {VOL_SHOCK} or above")
    if abs(daily_z) < Z_MIN:
        reasons.append(f"no daily trend: |daily z| below {Z_MIN:g}")
    return not reasons, state, tuple(reasons)


def compute_regime_gate(h1_bars: Sequence[Bar], now: datetime) -> RegimeGate:
    """Compute the regime gate from H1 candles, using only candles completed by ``now``."""
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if any(bar.start.tzinfo is None for bar in h1_bars):
        raise ValueError("every candle time must be timezone-aware")
    bars = sorted(h1_bars, key=lambda bar: bar.start)
    for i in range(1, len(bars)):
        if bars[i].start == bars[i - 1].start:
            raise ValueError(f"duplicate candle at {bars[i].start.isoformat()}")
    completed = [bar for bar in bars if bar.start + H1 <= now]
    needed = VOL_LOOKBACK + ATR_PERIOD - 1
    if len(completed) < needed:
        raise ValueError(f"need {needed} completed H1 bars for the vol ratio, got {len(completed)}")

    hourly = wilder_atr(completed)
    hourly_atr = hourly[-1]
    hourly_median = median(hourly[-VOL_LOOKBACK:])
    if hourly_median <= 0:
        raise ValueError("hourly ATR median is zero; check the candle data")
    vol_ratio = hourly_atr / hourly_median

    as_of = completed[-1].start + H1
    days = daily_bars(completed, as_of)
    if len(days) < SMA_PERIOD:
        raise ValueError(f"need {SMA_PERIOD} completed D1 sessions for SMA50, got {len(days)}")
    daily_atr = wilder_atr(days)[-1]
    if daily_atr <= 0:
        raise ValueError("daily ATR is zero; check the candle data")
    daily_close = days[-1].close
    daily_sma = sum(day.close for day in days[-SMA_PERIOD:]) / SMA_PERIOD
    daily_z = (daily_close - daily_sma) / daily_atr

    gate_open, state, reasons = classify(vol_ratio, daily_z)
    return RegimeGate(
        as_of=as_of,
        gate_open=gate_open,
        reasons=reasons,
        volatility_state=state,
        vol_ratio=vol_ratio,
        hourly_atr=hourly_atr,
        hourly_atr_median=hourly_median,
        open_hourly_atr_low=VOL_OPEN * hourly_median,
        open_hourly_atr_high=VOL_SHOCK * hourly_median,
        daily_z=daily_z,
        daily_close=daily_close,
        daily_sma50=daily_sma,
        daily_atr=daily_atr,
        last_completed_session=session_date(days[-1].start),
        h1_bars_used=len(completed),
        d1_sessions_used=len(days),
    )


def parse_time(value: str) -> datetime:
    """Parse ISO 8601 with a UTC offset (``Z`` allowed) or Unix seconds."""
    text = value.strip()
    if text.lstrip("-").isdigit():
        return datetime.fromtimestamp(int(text), tz=timezone.utc)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError(f"time without a UTC offset: {value!r}")
    return parsed


def load_csv(path: str) -> list[Bar]:
    """Load H1 candles from a CSV file with the columns time, high, low and close."""
    with open(path, newline="") as handle:
        return [
            Bar(
                start=parse_time(row["time"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
            )
            for row in csv.DictReader(handle)
        ]


def to_report(gate: RegimeGate) -> dict[str, object]:
    """Return the reading as a JSON-ready dict, with times in UTC and GST (Dubai)."""
    dubai = ZoneInfo("Asia/Dubai")
    return {
        "gate": "OPEN" if gate.gate_open else "CLOSED",
        "reasons": list(gate.reasons),
        "as_of_utc": gate.as_of.astimezone(timezone.utc).isoformat(),
        "as_of_gst": gate.as_of.astimezone(dubai).strftime("%Y-%m-%d %H:%M"),
        "volatility_state": gate.volatility_state,
        "vol_ratio": round(gate.vol_ratio, 4),
        "hourly_atr": round(gate.hourly_atr, 4),
        "hourly_atr_median": round(gate.hourly_atr_median, 4),
        "open_hourly_atr_range": [
            round(gate.open_hourly_atr_low, 4),
            round(gate.open_hourly_atr_high, 4),
        ],
        "daily_z": round(gate.daily_z, 4),
        "daily_close": gate.daily_close,
        "daily_sma50": round(gate.daily_sma50, 4),
        "daily_atr": round(gate.daily_atr, 4),
        "last_completed_session": gate.last_completed_session.isoformat(),
        "h1_bars_used": gate.h1_bars_used,
        "d1_sessions_used": gate.d1_sessions_used,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Print the regime-gate reading for a CSV of H1 candles as JSON."""
    parser = argparse.ArgumentParser(description="XAUUSD regime gate from H1 candles.")
    parser.add_argument("csv", help="H1 candles with the columns time, high, low, close")
    parser.add_argument("--now", help="current time, ISO 8601 with a UTC offset (default: now)")
    args = parser.parse_args(argv)
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    print(json.dumps(to_report(compute_regime_gate(load_csv(args.csv), now)), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
