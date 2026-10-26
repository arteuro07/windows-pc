"""
Standalone backtest for strategy_memory_liquidity.py.
Research only: reads OHLC CSV and never connects to MetaTrader or places orders.

CSV columns required: time, open, high, low, close
Optional column: spread (price units, not points). Timestamps must be oldest -> newest.
Assumption: signal on a closed candle, entry at next candle open. If SL and TP are
both touched within one candle, the conservative assumption is that SL is hit first.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from strategy_memory_liquidity import generate_signal


def load_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"open", "high", "low", "close"}
        fields = {name.strip().lower() for name in (reader.fieldnames or [])}
        if not required.issubset(fields):
            raise ValueError("CSV must contain open, high, low, close columns (and preferably time).")
        for row in reader:
            normalized = {str(k).strip().lower(): v for k, v in row.items() if k is not None}
            try:
                item: dict[str, Any] = {k: float(normalized[k]) for k in required}
                item["time"] = normalized.get("time", normalized.get("timestamp", str(len(rows))))
                item["spread"] = float(normalized.get("spread") or 0.0)
            except (TypeError, ValueError, KeyError):
                continue
            if item["high"] < max(item["open"], item["close"], item["low"]):
                continue
            if item["low"] > min(item["open"], item["close"], item["high"]):
                continue
            rows.append(item)
    if len(rows) < 100:
        raise ValueError(f"Only {len(rows)} valid candles loaded; provide at least 100.")
    return rows


def run_backtest(rows: list[dict[str, Any]], risk_fraction: float = 0.0025) -> dict[str, Any]:
    if not 0 < risk_fraction <= 0.01:
        raise ValueError("risk_fraction must be > 0 and <= 1% (default 0.25%).")
    candles = [{k: row[k] for k in ("open", "high", "low", "close")} for row in rows]
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    trades: list[dict[str, Any]] = []
    i = 35
    while i < len(rows) - 1:
        signal = generate_signal(
            candles[:i + 1],
            spread=float(rows[i].get("spread", 0.0)),
        )
        side = signal["side"]
        if side not in ("BUY", "SELL"):
            i += 1
            continue

        entry = float(rows[i + 1]["open"])
        stop_ref = float(signal["stop_reference"])
        target_ref = float(signal["target_reference"])
        risk_per_unit = abs(entry - stop_ref)
        if risk_per_unit <= 0:
            i += 1
            continue
        # Keep the original stop distance around the next-open fill.
        stop = stop_ref
        target = entry + (abs(target_ref - float(signal["entry_reference"])) if side == "BUY" else -abs(float(signal["entry_reference"]) - target_ref))
        if side == "BUY" and (stop >= entry or target <= entry):
            i += 1
            continue
        if side == "SELL" and (stop <= entry or target >= entry):
            i += 1
            continue

        exit_price = None
        exit_reason = "end_of_data"
        exit_index = len(rows) - 1
        for j in range(i + 1, len(rows)):
            bar = rows[j]
            if side == "BUY":
                hit_sl = float(bar["low"]) <= stop
                hit_tp = float(bar["high"]) >= target
            else:
                hit_sl = float(bar["high"]) >= stop
                hit_tp = float(bar["low"]) <= target
            if hit_sl:
                exit_price, exit_reason, exit_index = stop, "stop_loss", j
                break
            if hit_tp:
                exit_price, exit_reason, exit_index = target, "take_profit", j
                break

        if exit_price is None:
            exit_price = float(rows[exit_index]["close"])
        pnl_r = ((exit_price - entry) / risk_per_unit) if side == "BUY" else ((entry - exit_price) / risk_per_unit)
        # Fixed-fractional approximation; ignores contract sizing, commissions and swap.
        equity *= max(0.0, 1.0 + risk_fraction * pnl_r)
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak - equity) / peak if peak else 0.0)
        trades.append({
            "entry_time": rows[i + 1]["time"],
            "exit_time": rows[exit_index]["time"],
            "side": side,
            "entry": round(entry, 8),
            "stop": round(stop, 8),
            "target": round(target, 8),
            "exit": round(float(exit_price), 8),
            "exit_reason": exit_reason,
            "result_R": round(pnl_r, 4),
            "equity_factor": round(equity, 8),
            "signal_score": signal["score"],
        })
        i = exit_index + 1

    wins = sum(1 for t in trades if t["result_R"] > 0)
    losses = sum(1 for t in trades if t["result_R"] <= 0)
    gross_win_r = sum(t["result_R"] for t in trades if t["result_R"] > 0)
    gross_loss_r = -sum(t["result_R"] for t in trades if t["result_R"] < 0)
    summary = {
        "candles": len(rows),
        "trades": len(trades),
        "wins": wins,
        "losses_or_breakeven": losses,
        "win_rate_pct": round(100 * wins / len(trades), 2) if trades else 0.0,
        "net_R": round(sum(t["result_R"] for t in trades), 4),
        "profit_factor_R": round(gross_win_r / gross_loss_r, 4) if gross_loss_r else None,
        "equity_change_pct_approx": round((equity - 1.0) * 100, 2),
        "max_drawdown_pct_approx": round(max_dd * 100, 2),
        "risk_fraction_per_trade": risk_fraction,
        "limitations": [
            "Research approximation, not a broker-accurate MT5 simulation.",
            "No commission, swap, slippage, variable spread, contract-size or margin model.",
            "Intrabar stop-loss is assumed first if both SL and TP are touched.",
            "No out-of-sample claim until separate unseen data is tested."
        ],
        "trades_detail": trades,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest EURO liquidity-memory signals (research only).")
    parser.add_argument("csv_file", help="OHLC CSV file")
    parser.add_argument("--risk", type=float, default=0.0025, help="risk fraction per trade, default 0.0025 (0.25%)")
    parser.add_argument("--out", default="backtest_memory_liquidity_results.json", help="output JSON path")
    args = parser.parse_args()
    rows = load_csv(Path(args.csv_file))
    result = run_backtest(rows, risk_fraction=args.risk)
    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "trades_detail"}, indent=2))
    print(f"Full report saved to: {args.out}")


if __name__ == "__main__":
    main()
