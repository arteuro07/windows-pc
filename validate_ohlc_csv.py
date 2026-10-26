#!/usr/bin/env python3
"""Validate a historical OHLC CSV before running the EURO research backtest.

This tool does not download market data and does not connect to a broker.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an OHLC CSV for research backtesting.")
    parser.add_argument("csv_file")
    args = parser.parse_args()
    path = Path(args.csv_file)
    if not path.is_file():
        print(f"ERROR: file not found: {path}")
        return 2

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            print("ERROR: CSV header is missing.")
            return 2
        names = {name.strip().lower() for name in reader.fieldnames}
        missing = {"open", "high", "low", "close"} - names
        if missing:
            print("ERROR: missing required columns:", ", ".join(sorted(missing)))
            print("Expected at least: time,open,high,low,close (spread optional)")
            return 2
        time_col = "time" if "time" in names else ("timestamp" if "timestamp" in names else None)
        rows = []
        invalid = 0
        previous_time = None
        out_of_order = 0
        for line_no, row in enumerate(reader, start=2):
            normalized = {str(k).strip().lower(): v for k, v in row.items() if k is not None}
            try:
                o, h, l, c = (float(normalized[k]) for k in ("open", "high", "low", "close"))
                if not all(map(lambda x: x == x and abs(x) != float("inf"), (o, h, l, c))):
                    raise ValueError("non-finite value")
                if h < max(o, c, l) or l > min(o, c, h):
                    raise ValueError("inconsistent OHLC")
                if "spread" in normalized and normalized["spread"].strip():
                    spread = float(normalized["spread"])
                    if spread < 0 or spread != spread or abs(spread) == float("inf"):
                        raise ValueError("invalid spread")
                if time_col and normalized.get(time_col):
                    stamp = normalized[time_col].strip()
                    try:
                        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                    except ValueError:
                        parsed = None
                    if parsed is not None:
                        if previous_time is not None and parsed < previous_time:
                            out_of_order += 1
                        previous_time = parsed
                rows.append((o, h, l, c))
            except (TypeError, ValueError, KeyError):
                invalid += 1

    print(f"File: {path}")
    print(f"Valid candles: {len(rows)}")
    print(f"Invalid rows skipped: {invalid}")
    print(f"Chronological order violations detected: {out_of_order}")
    print(f"Spread column: {'present' if 'spread' in names else 'absent (treated as zero by backtest)'}")
    if len(rows) < 100:
        print("RESULT: NOT READY — at least 100 valid candles are required; substantially more are recommended.")
        return 1
    if out_of_order:
        print("RESULT: CHECK REQUIRED — timestamps appear out of order. Sort oldest to newest before testing.")
        return 1
    if invalid:
        print("RESULT: CHECK REQUIRED — invalid rows were skipped; inspect the source CSV.")
        return 1
    print("RESULT: BASIC CHECK PASSED — this only checks file structure, not data authenticity or strategy profitability.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
