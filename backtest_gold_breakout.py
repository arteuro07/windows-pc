"""Backtest historique conservateur de Cassure Or (sans aucun ordre).

Utilise des bougies M1 MT5, construit le range serveur 00:00-07:00,
arme une cassure jusqu'à 08:00, SL de 1 % et sortie à 18:00.
Les timestamps MT5 sont traités comme UTC puis décalés de BRK_UTC_OFFSET_HOURS
pour reconstruire l'heure serveur. Cette hypothèse doit être vérifiée pour le courtier.

Limites : OHLC M1 ne reconstitue pas le chemin des ticks; si les deux côtés cassent
dans la même minute, la journée est ignorée. Les résultats sont des R multiples,
pas une simulation exacte de l'exécution ou des lots.
"""
import os
import sys
import json
import time
import datetime as dt
from collections import defaultdict

SYMBOL = os.environ.get("BRK_SYMBOL", "XAUUSD")
START = os.environ.get("BT_START", "2022-01-01")
END = os.environ.get("BT_END", "2026-10-20")
UTC_OFFSET = float(os.environ.get("BRK_UTC_OFFSET_HOURS", "0"))
SPREAD = float(os.environ.get("BRK_SPREAD", "0.30"))
SL_PCT = float(os.environ.get("BRK_SL_PCT", "0.01"))
RANGE_START_H = 0
RANGE_END_H = 7
LAST_ENTRY_H = 8
CLOSE_H = 18
MIN_RANGE_BARS = 24  # 6 heures de données M15 minimum
os.makedirs("out", exist_ok=True)


def log(message):
    line = time.strftime("%H:%M:%S ") + message
    print(line, flush=True)
    with open("out/backtest_gold_breakout.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_day(s):
    return dt.datetime.strptime(s, "%Y-%m-%d").date()


def server_time(unix_ts):
    return dt.datetime.fromtimestamp(int(unix_ts), dt.timezone.utc).replace(tzinfo=None) + dt.timedelta(hours=UTC_OFFSET)


def epoch_utc(naive_utc):
    """Convert a naive datetime already expressed in UTC to Unix time without host-local timezone effects."""
    return naive_utc.replace(tzinfo=dt.timezone.utc).timestamp()


def clean_rates(rates):
    if rates is None:
        return []
    out = []
    for x in rates:
        out.append({
            "time": int(x["time"]),
            "open": float(x["open"]),
            "high": float(x["high"]),
            "low": float(x["low"]),
            "close": float(x["close"]),
        })
    return out


def backtest_day(day, m1, m15):
    start = dt.datetime.combine(day, dt.time(0)) - dt.timedelta(hours=UTC_OFFSET)
    end = dt.datetime.combine(day, dt.time(CLOSE_H)) - dt.timedelta(hours=UTC_OFFSET)
    day_m1 = [b for b in m1 if epoch_utc(start) <= b["time"] < epoch_utc(end)]
    range_start = dt.datetime.combine(day, dt.time(RANGE_START_H)) - dt.timedelta(hours=UTC_OFFSET)
    range_end = dt.datetime.combine(day, dt.time(RANGE_END_H)) - dt.timedelta(hours=UTC_OFFSET)
    range_bars = [b for b in m15 if epoch_utc(range_start) <= b["time"] < epoch_utc(range_end)]
    if len(range_bars) < MIN_RANGE_BARS:
        return {"date": str(day), "status": "skip_range_incomplet", "range_bars": len(range_bars)}
    hi = max(b["high"] for b in range_bars)
    lo = min(b["low"] for b in range_bars)
    if hi <= lo:
        return {"date": str(day), "status": "skip_range_invalide"}
    entry_deadline = dt.datetime.combine(day, dt.time(LAST_ENTRY_H)) - dt.timedelta(hours=UTC_OFFSET)
    close_time = dt.datetime.combine(day, dt.time(CLOSE_H)) - dt.timedelta(hours=UTC_OFFSET)
    entry = None
    side = 0
    for b in day_m1:
        t = dt.datetime.fromtimestamp(b["time"], dt.timezone.utc).replace(tzinfo=None)
        if t < range_end or t >= entry_deadline:
            continue
        buy_hit = b["high"] + SPREAD >= hi
        sell_hit = b["low"] <= lo
        if buy_hit and sell_hit:
            return {"date": str(day), "status": "skip_both_sides_same_minute", "range_high": hi, "range_low": lo}
        if buy_hit:
            side = 1
            # OHLC is treated as Bid; a BUY executes at Ask.
            entry = max(hi, b["open"] + SPREAD)
            entry = max(entry, b["low"] + SPREAD)
            entry_time = b["time"]
            break
        if sell_hit:
            side = -1
            entry = min(lo, b["open"])
            entry = min(entry, b["high"])
            entry_time = b["time"]
            break
    if entry is None:
        return {"date": str(day), "status": "no_breakout", "range_high": hi, "range_low": lo}
    sl = entry * (1 - side * SL_PCT)
    risk_price = abs(entry - sl)
    if risk_price <= 0:
        return {"date": str(day), "status": "skip_invalid_sl"}
    # Search after entry. OHLC ambiguity is handled pessimistically: SL takes priority.
    exit_price = None
    exit_reason = None
    exit_ts = None
    for b in day_m1:
        if b["time"] < entry_time:
            continue
        t = dt.datetime.fromtimestamp(b["time"], dt.timezone.utc).replace(tzinfo=None)
        if t >= close_time:
            break
        if side == 1:
            if b["low"] <= sl:
                exit_price = min(b["open"], sl)  # pessimistic gap handling
                exit_reason = "SL"
                exit_ts = b["time"]
                break
        else:
            # For SELL, stop is triggered by Ask = Bid + spread.
            if b["high"] + SPREAD >= sl:
                exit_price = max(b["open"] + SPREAD, sl)
                exit_reason = "SL"
                exit_ts = b["time"]
                break
    if exit_price is None:
        eligible = [b for b in day_m1 if b["time"] >= entry_time and b["time"] < close_time]
        if not eligible:
            return {"date": str(day), "status": "skip_no_exit_data"}
        last = eligible[-1]
        exit_price = last["close"] if side == 1 else last["close"] + SPREAD
        exit_reason = "time"
        exit_ts = last["time"]
    # Entry/exit sides already model the spread: BUY enters Ask/exits Bid; SELL enters Bid/exits Ask.
    pnl_price = (exit_price - entry) * side
    r_mult = pnl_price / risk_price
    return {
        "date": str(day), "status": "trade", "side": "BUY" if side == 1 else "SELL",
        "range_high": round(hi, 5), "range_low": round(lo, 5),
        "entry": round(entry, 5), "sl": round(sl, 5), "exit": round(exit_price, 5),
        "entry_time_utc": dt.datetime.fromtimestamp(entry_time, dt.timezone.utc).isoformat(),
        "exit_time_utc": dt.datetime.fromtimestamp(exit_ts, dt.timezone.utc).isoformat(),
        "exit_reason": exit_reason, "spread": SPREAD, "R": round(r_mult, 5),
    }


def summarize(trades):
    if not trades:
        return {"trades": 0, "total_R": 0.0}
    vals = [float(t["R"]) for t in trades]
    wins = [x for x in vals if x > 0]
    losses = [x for x in vals if x <= 0]
    eq = peak = max_dd = 0.0
    for x in vals:
        eq += x
        peak = max(peak, eq)
        max_dd = max(max_dd, peak - eq)
    gross_win = sum(wins)
    gross_loss = -sum(losses)
    return {
        "trades": len(vals),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": round(100 * len(wins) / len(vals), 2),
        "total_R": round(sum(vals), 3),
        "avg_R": round(sum(vals) / len(vals), 4),
        "profit_factor": round(gross_win / gross_loss, 3) if gross_loss else None,
        "max_drawdown_R": round(max_dd, 3),
    }


def main():
    global SPREAD  # la sensibilité au spread ajuste temporairement cette configuration
    import MetaTrader5 as mt5
    start_day, end_day = parse_day(START), parse_day(END)
    if end_day < start_day:
        raise ValueError("BT_END doit être postérieur ou égal à BT_START")
    if SPREAD < 0 or SL_PCT <= 0:
        raise ValueError("Spread doit être >= 0 et SL_PCT > 0")
    path = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    ok = False
    for attempt in range(1, 5):
        ok = mt5.initialize(path=path, login=int(os.environ["MT5_LOGIN"]),
                            password=os.environ["MT5_PASSWORD"], server=os.environ["MT5_SERVER"],
                            timeout=120000)
        if ok:
            break
        log(f"Connexion MT5 {attempt}/4 échouée: {mt5.last_error()}")
        mt5.shutdown()
        time.sleep(15)
    if not ok:
        log("ERREUR: connexion MT5 impossible")
        sys.exit(1)
    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        log(f"Terminal MT5: {terminal}")
        log(f"Compte MT5 connecté: {account is not None}; serveur={getattr(account, 'server', None) if account else None}")
        all_symbols = mt5.symbols_get() or []
        gold_candidates = [s.name for s in all_symbols if ("XAU" in s.name.upper() or "GOLD" in s.name.upper())]
        log(f"Symboles contenant XAU/GOLD (premiers 30): {gold_candidates[:30]}")
        info = mt5.symbol_info(SYMBOL)
        if info is None:
            candidates = [s.name for s in all_symbols if s.name.upper().startswith(SYMBOL.upper())]
            if not candidates:
                raise RuntimeError(f"Symbole introuvable: {SYMBOL}. Candidats or: {gold_candidates[:30]}")
            symbol = candidates[0]
        else:
            symbol = SYMBOL
        selected = mt5.symbol_select(symbol, True)
        log(f"Symbole choisi={symbol}; symbol_select={selected}; info={mt5.symbol_info(symbol)}")
        if not selected:
            raise RuntimeError(f"Impossible d'activer le symbole {symbol}: {mt5.last_error()}")
        # UTC-aware datetimes: MT5 Python API expects UTC for historical requests.
        utc_start = dt.datetime.combine(start_day, dt.time(0), tzinfo=dt.timezone.utc) - dt.timedelta(hours=UTC_OFFSET)
        utc_end = dt.datetime.combine(end_day + dt.timedelta(days=1), dt.time(0), tzinfo=dt.timezone.utc) - dt.timedelta(hours=UTC_OFFSET)
        log(f"Backtest sans ordres: {symbol}, {START} -> {END}, offset serveur={UTC_OFFSET}h, spread={SPREAD}")
        m1 = clean_rates(mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, utc_start, utc_end))
        m15 = clean_rates(mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, utc_start, utc_end))
        log(f"Historique reçu: M1={len(m1)} M15={len(m15)}; erreur MT5 après requêtes={mt5.last_error()}")
        if not m1 or not m15:
            recent_m1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 10)
            recent_m15 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 10)
            log(f"Test historique récent: M1={0 if recent_m1 is None else len(recent_m1)}; M15={0 if recent_m15 is None else len(recent_m15)}; erreur MT5={mt5.last_error()}")
        if len(m1) < 1000 or len(m15) < 100:
            raise RuntimeError("Historique insuffisant. Voir les lignes Terminal, Symboles, symbol_select et erreur MT5 ci-dessus.")
        days = []
        d = start_day
        while d <= end_day:
            if d.weekday() < 5:
                days.append(backtest_day(d, m1, m15))
            d += dt.timedelta(days=1)
        trades = [x for x in days if x.get("status") == "trade"]
        result = {
            "config": {"symbol": symbol, "start": START, "end": END, "server_utc_offset_hours": UTC_OFFSET,
                       "spread_price_units": SPREAD, "sl_pct": SL_PCT,
                       "range_server_time": "00:00-07:00", "entry_server_time": "07:00-08:00",
                       "close_server_time": "18:00", "model": "M1 OHLC approximation; no orders sent"},
            "summary": summarize(trades),
            "by_year": {},
            "by_month": {},
            "days": days,
        }
        for label_fn, key in (
            (lambda s: s[:4], "by_year"),
            (lambda s: s[:7], "by_month"),
        ):
            groups = defaultdict(list)
            for t in trades:
                groups[label_fn(t["date"])].append(t)
            result[key] = {k: summarize(v) for k, v in sorted(groups.items())}
        # Spread robustness: recompute using wider spreads. Entry triggers and exits are re-simulated.
        sensitivity = {}
        for factor in (1.0, 1.5, 2.0):
            old = SPREAD
            SPREAD = old * factor
            try:
                alt = [backtest_day(d, m1, m15) for d in days_list(start_day, end_day)]
                sensitivity[f"{factor:.1f}x"] = summarize([x for x in alt if x.get("status") == "trade"])
            finally:
                SPREAD = old
        result["spread_sensitivity"] = sensitivity
        with open("out/backtest_gold_breakout.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        with open("out/backtest_gold_breakout_trades.csv", "w", encoding="utf-8", newline="") as f:
            import csv
            keys = ["date", "status", "side", "range_high", "range_low", "entry", "sl", "exit",
                    "entry_time_utc", "exit_time_utc", "exit_reason", "spread", "R"]
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(days)
        log("RÉSULTAT GLOBAL: " + json.dumps(result["summary"], ensure_ascii=False))
        log("SENSIBILITÉ SPREAD: " + json.dumps(sensitivity, ensure_ascii=False))
        log("Fichiers générés: out/backtest_gold_breakout.json et out/backtest_gold_breakout_trades.csv")
    finally:
        mt5.shutdown()


def days_list(start_day, end_day):
    out = []
    d = start_day
    while d <= end_day:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


if __name__ == "__main__":
    main()
