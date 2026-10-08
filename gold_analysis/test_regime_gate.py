"""Tests for the XAUUSD regime gate."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from gold_analysis.regime_gate import (
    H1,
    NEW_YORK,
    Bar,
    classify,
    compute_regime_gate,
    main,
    parse_time,
    session_date,
    wilder_atr,
)

# Sunday 4 January 2026, 18:00 New York (EST): the weekly open.
FIRST_OPEN = datetime(2026, 1, 4, 23, 0, tzinfo=timezone.utc)


def market_hours(count: int) -> list[datetime]:
    """Return ``count`` H1 open times inside gold market hours, starting at FIRST_OPEN."""
    times: list[datetime] = []
    current = FIRST_OPEN
    while len(times) < count:
        local = current.astimezone(NEW_YORK)
        weekday, hour = local.weekday(), local.hour
        closed = (
            weekday == 5
            or (weekday == 6 and hour < 18)
            or (weekday == 4 and hour >= 17)
            or hour == 17
        )
        if not closed:
            times.append(current)
        current += H1
    return times


def synthetic(
    step: float, last_range: float, count: int = 1600, last_bars: int = 60
) -> tuple[list[Bar], datetime]:
    """Build H1 candles whose close moves ``step`` per candle and whose range is 1.0.

    The last ``last_bars`` candles use ``last_range`` instead. The series spans the March daylight
    saving change in New York. Returns the candles and a time just after the last one closes.
    """
    times = market_hours(count)
    bars = []
    for i, start in enumerate(times):
        candle_range = last_range if i >= count - last_bars else 1.0
        mid = 2000.0 + i * step
        bars.append(
            Bar(start=start, high=mid + candle_range / 2, low=mid - candle_range / 2, close=mid)
        )
    return bars, times[-1] + H1


def test_wilder_atr_matches_hand_computation() -> None:
    ranges = [2.0, 4.0, 6.0, 8.0, 10.0]
    bars = [
        Bar(start=FIRST_OPEN + i * H1, high=100 + r / 2, low=100 - r / 2, close=100.0)
        for i, r in enumerate(ranges)
    ]
    assert wilder_atr(bars, period=3) == pytest.approx([4.0, 16 / 3, 62 / 9])


@pytest.mark.parametrize(
    ("utc", "expected"),
    [
        (datetime(2026, 7, 15, 20, 0, tzinfo=timezone.utc), date(2026, 7, 15)),  # 16:00 EDT.
        (datetime(2026, 7, 15, 21, 0, tzinfo=timezone.utc), date(2026, 7, 16)),  # 17:00 EDT.
        (datetime(2026, 7, 15, 22, 0, tzinfo=timezone.utc), date(2026, 7, 16)),  # 18:00 EDT.
        (datetime(2026, 1, 15, 21, 0, tzinfo=timezone.utc), date(2026, 1, 15)),  # 16:00 EST.
        (datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc), date(2026, 1, 16)),  # 18:00 EST.
    ],
)
def test_session_date_rolls_at_17_new_york(utc: datetime, expected: date) -> None:
    assert session_date(utc) == expected


@pytest.mark.parametrize(
    ("vol_ratio", "daily_z", "is_open", "state"),
    [
        (1.25, 1.0, True, "active"),
        (1.9999, -1.0, True, "active"),
        (1.2499, 3.0, False, "quiet"),
        (2.0, 3.0, False, "shock"),
        (1.5, 0.9999, False, "active"),
    ],
)
def test_classify_boundaries(vol_ratio: float, daily_z: float, is_open: bool, state: str) -> None:
    gate_open, volatility_state, reasons = classify(vol_ratio, daily_z)
    assert (gate_open, volatility_state) == (is_open, state)
    assert bool(reasons) is not is_open


def test_gate_open_in_active_volatility_with_a_daily_uptrend() -> None:
    bars, now = synthetic(step=0.1, last_range=1.5)
    gate = compute_regime_gate(bars, now)
    assert gate.gate_open
    assert gate.volatility_state == "active"
    assert 1.25 <= gate.vol_ratio < 2.0
    assert gate.hourly_atr_median == pytest.approx(1.0)
    assert gate.daily_z >= 1.0
    assert gate.d1_sessions_used >= 50


def test_gate_open_with_a_daily_downtrend() -> None:
    bars, now = synthetic(step=-0.1, last_range=1.5)
    gate = compute_regime_gate(bars, now)
    assert gate.gate_open
    assert gate.daily_z <= -1.0


@pytest.mark.parametrize(
    ("step", "last_range", "reason_start"),
    [
        (0.1, 1.0, "quiet volatility"),
        (0.1, 3.0, "shock volatility"),
        (0.0, 1.5, "no daily trend"),
    ],
)
def test_gate_closed(step: float, last_range: float, reason_start: str) -> None:
    bars, now = synthetic(step=step, last_range=last_range)
    gate = compute_regime_gate(bars, now)
    assert not gate.gate_open
    assert len(gate.reasons) == 1
    assert gate.reasons[0].startswith(reason_start)


def test_forming_candle_is_ignored() -> None:
    bars, now = synthetic(step=0.1, last_range=1.5)
    gate = compute_regime_gate(bars, now - timedelta(minutes=30))
    assert gate.h1_bars_used == len(bars) - 1
    assert gate.as_of == bars[-2].start + H1


def test_too_little_hourly_history_raises() -> None:
    bars, now = synthetic(step=0.1, last_range=1.5, count=400)
    with pytest.raises(ValueError, match="completed H1 bars"):
        compute_regime_gate(bars, now)


def test_too_few_daily_sessions_raises() -> None:
    bars, now = synthetic(step=0.1, last_range=1.5, count=600)
    with pytest.raises(ValueError, match="completed D1 sessions"):
        compute_regime_gate(bars, now)


def test_duplicate_candles_are_rejected() -> None:
    bars, now = synthetic(step=0.1, last_range=1.5)
    with pytest.raises(ValueError, match="duplicate"):
        compute_regime_gate([*bars, bars[-1]], now)


def test_parse_time_needs_a_utc_offset() -> None:
    with pytest.raises(ValueError, match="UTC offset"):
        parse_time("2026-10-08T12:00:00")
    assert parse_time("2026-10-08T12:00:00Z") == datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
    assert parse_time("1791460800") == datetime.fromtimestamp(1791460800, tz=timezone.utc)


def test_command_line_prints_the_reading(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bars, now = synthetic(step=0.1, last_range=1.5)
    path = tmp_path / "h1.csv"
    rows = ["time,open,high,low,close"] + [
        f"{bar.start.isoformat()},{bar.close},{bar.high},{bar.low},{bar.close}" for bar in bars
    ]
    path.write_text("\n".join(rows) + "\n")
    assert main([str(path), "--now", now.isoformat()]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["gate"] == "OPEN"
    assert report["volatility_state"] == "active"
    assert report["reasons"] == []
