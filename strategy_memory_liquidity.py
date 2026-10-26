"""
EURO — Mémoire de liquidité v1
Signal research module only: NO MetaTrader connection and NO order execution.

Input candles are dictionaries with: open, high, low, close.
Expected order: oldest -> newest. The last candle must be CLOSED.
All price values must use the broker's actual symbol prices.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class Signal:
    side: str                 # BUY, SELL, or NONE
    entry_reference: float | None
    stop_reference: float | None
    target_reference: float | None
    score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _valid_candle(c: Mapping[str, Any]) -> bool:
    try:
        o, h, l, cl = (float(c[k]) for k in ("open", "high", "low", "close"))
        return all(map(_finite, (o, h, l, cl))) and h >= max(o, cl, l) and l <= min(o, cl, h)
    except (KeyError, TypeError, ValueError):
        return False


def _finite(value: float) -> bool:
    return value == value and abs(value) != float("inf")


def _atr(candles: Sequence[Mapping[str, Any]], period: int) -> float | None:
    if len(candles) < period + 1:
        return None
    ranges = []
    for i in range(len(candles) - period, len(candles)):
        c = candles[i]
        prev_close = float(candles[i - 1]["close"])
        ranges.append(max(
            float(c["high"]) - float(c["low"]),
            abs(float(c["high"]) - prev_close),
            abs(float(c["low"]) - prev_close),
        ))
    value = sum(ranges) / len(ranges)
    return value if value > 0 and _finite(value) else None


def _level_memory(candles: Sequence[Mapping[str, Any]], lookback: int) -> tuple[float, float, int, int]:
    """Return recent high/low and approximate prior reactions near those levels."""
    window = candles[-lookback-1:-1]
    recent_high = max(float(c["high"]) for c in window)
    recent_low = min(float(c["low"]) for c in window)
    # A reaction is counted when a prior wick approaches a level and closes back inside.
    scale = max((recent_high - recent_low) * 0.04, 1e-12)
    high_reactions = sum(
        1 for c in window
        if abs(float(c["high"]) - recent_high) <= scale
        and float(c["close"]) < float(c["high"])
    )
    low_reactions = sum(
        1 for c in window
        if abs(float(c["low"]) - recent_low) <= scale
        and float(c["close"]) > float(c["low"])
    )
    return recent_high, recent_low, high_reactions, low_reactions


def generate_signal(
    candles_m1: Sequence[Mapping[str, Any]],
    candles_m15: Sequence[Mapping[str, Any]] | None = None,
    *,
    lookback: int = 20,
    atr_period: int = 14,
    min_wick_atr: float = 0.15,
    max_reclaim_atr: float = 0.35,
    min_score: float = 0.60,
    spread: float = 0.0,
    reward_risk: float = 1.8,
) -> dict[str, Any]:
    """
    Evaluate one closed M1 candle for a liquidity sweep + reclaim.

    Returns a serializable Signal dictionary. This function NEVER places orders.
    M15 filter: if supplied, requires at least 5 candles and rejects a setup
    when the latest M15 candle has a strong body against the intended direction.
    """
    if lookback < 5 or atr_period < 2 or reward_risk <= 0 or spread < 0:
        return Signal("NONE", None, None, None, 0.0, "Invalid parameters").to_dict()
    if len(candles_m1) < max(lookback + 1, atr_period + 1):
        return Signal("NONE", None, None, None, 0.0, "Insufficient M1 history").to_dict()
    if not all(_valid_candle(c) for c in candles_m1[-max(lookback + 1, atr_period + 1):]):
        return Signal("NONE", None, None, None, 0.0, "Invalid M1 candle data").to_dict()
    if candles_m15 is not None:
        if len(candles_m15) < 5 or not all(_valid_candle(c) for c in candles_m15[-5:]):
            return Signal("NONE", None, None, None, 0.0, "Insufficient/invalid M15 filter data").to_dict()

    atr = _atr(candles_m1, atr_period)
    if atr is None:
        return Signal("NONE", None, None, None, 0.0, "ATR unavailable").to_dict()

    high, low, high_memory, low_memory = _level_memory(candles_m1, lookback)
    c = candles_m1[-1]
    o, h, l, close = (float(c[k]) for k in ("open", "high", "low", "close"))
    candle_range = h - l
    if candle_range <= 0:
        return Signal("NONE", None, None, None, 0.0, "Zero-range candle").to_dict()

    lower_wick = min(o, close) - l
    upper_wick = h - max(o, close)
    reclaim_distance = max_reclaim_atr * atr

    # BUY: price swept below a prior low, then closed back above that level.
    buy = l < low and close > low and lower_wick >= min_wick_atr * atr
    # SELL: price swept above a prior high, then closed back below that level.
    sell = h > high and close < high and upper_wick >= min_wick_atr * atr

    if buy and sell:
        return Signal("NONE", None, None, None, 0.0, "Ambiguous two-sided sweep").to_dict()

    if not buy and not sell:
        return Signal("NONE", None, None, None, 0.0, "No confirmed sweep and reclaim").to_dict()

    side = "BUY" if buy else "SELL"
    wick = lower_wick if buy else upper_wick
    # Score rewards clear rejection and repeated historical reactions, with a cap.
    memory_count = low_memory if buy else high_memory
    wick_score = min(wick / max(atr, 1e-12), 1.0)
    memory_score = min(memory_count / 4.0, 1.0)
    reclaim_score = 1.0 if abs(close - (low if buy else high)) <= reclaim_distance else 0.5
    score = 0.50 * wick_score + 0.25 * memory_score + 0.25 * reclaim_score

    if candles_m15 is not None:
        m = candles_m15[-1]
        m_open, m_close = float(m["open"]), float(m["close"])
        m_atr = _atr(candles_m15, min(14, len(candles_m15) - 1))
        if m_atr and abs(m_close - m_open) >= 0.75 * m_atr:
            if (side == "BUY" and m_close < m_open) or (side == "SELL" and m_close > m_open):
                return Signal("NONE", None, None, None, score, "Rejected by strong opposing M15 candle").to_dict()

    if score < min_score:
        return Signal("NONE", None, None, None, score, "Setup score below threshold").to_dict()

    # Conservative reference stop beyond the sweep wick plus spread allowance.
    buffer = max(spread, 0.05 * atr)
    entry = close
    stop = (l - buffer) if buy else (h + buffer)
    risk = abs(entry - stop)
    if risk <= 0 or not _finite(risk):
        return Signal("NONE", None, None, None, score, "Invalid calculated risk").to_dict()
    target = entry + reward_risk * risk if buy else entry - reward_risk * risk
    return Signal(side, entry, stop, target, round(score, 4),
                  "Closed-candle sweep/reclaim; research signal only").to_dict()
