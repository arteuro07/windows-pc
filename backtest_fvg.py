"""Backtest de la strategie FVG sur l'historique MT5 (XAUUSD). Aucun ordre passe."""
import os, sys, time, json, bisect, datetime as dt
import fvg

OFF = int(os.environ.get("BROKER_PARIS_OFFSET", "-1"))
SPREAD = float(os.environ.get("BT_SPREAD", "0.25"))
os.makedirs("out", exist_ok=True)

def log(m):
    line = time.strftime("%H:%M:%S ") + m
    print(line, flush=True)
    with open("out/backtest.log", "a") as f:
        f.write(line + "\n")

def ptime(t):
    return dt.datetime.utcfromtimestamp(t) + dt.timedelta(hours=OFF)

def simulate(sl_usd, m15, h1, d1, trail=True):
    h1t = [x["time"] + 3600 for x in h1]
    d1t = [x["time"] for x in d1]
    used, pend, pos, trades = set(), None, None, []
    day, per_day, hcache = None, 0, {}
    n = len(m15)

    def bias_at(t):
        k = bisect.bisect_right(h1t, t)
        if k < 30:
            return 0
        if k not in hcache:
            hcache[k] = fvg.bias_from(h1[max(0, k - 300):k])
        return hcache[k]

    def close_pos(i, price, why):
        nonlocal pos
        side = pos["side"]
        pnl = pos["real"] + (price - pos["entry"]) * side * pos["rem"] - SPREAD
        trades.append({"open": pos["t0"], "close": m15[i]["time"], "side": side, "entry": pos["entry"],
                       "exit": price, "pnl": pnl, "R": pnl / sl_usd, "why": why})
        pos = None

    for i in range(130, n):
        b = m15[i]
        pt = ptime(b["time"])
        if pend:
            if i > pend["exp"] or bias_at(b["time"]) != pend["side"] or not fvg.in_session(pt):
                pend = None
            else:
                s, e = pend["side"], pend["entry"]
                hit = b["low"] <= e if s > 0 else b["high"] >= e
                if hit:
                    fill = min(b["open"], e) if s > 0 else max(b["open"], e)
                    pos = {"side": s, "entry": fill, "sl": fill - s * sl_usd, "rem": 1.0,
                           "real": 0.0, "half": False, "t0": b["time"]}
                    pend = None
        if pos:
            s = pos["side"]
            if not fvg.in_session(pt):
                close_pos(i, b["open"], "fin session")
            else:
                if trail and pos["half"]:
                    sw = fvg.last_swing(m15[i - 130:i], s)
                    px = m15[i - 1]["close"]
                    if sw is not None and (sw - pos["sl"]) * s > 0 and (px - sw) * s > 0.1:
                        pos["sl"] = sw
                hit_sl = b["low"] <= pos["sl"] if s > 0 else b["high"] >= pos["sl"]
                if hit_sl:
                    px = min(b["open"], pos["sl"]) if s > 0 else max(b["open"], pos["sl"])
                    close_pos(i, px, "stop")
                else:
                    reach = (b["high"] - pos["entry"] if s > 0 else pos["entry"] - b["low"])
                    if not pos["half"] and reach >= sl_usd:
                        pos["real"] += sl_usd * 0.5
                        pos["rem"] = 0.5
                        pos["half"] = True
                        pos["sl"] = pos["entry"] + s * fvg.BE_PLUS
                        back = b["low"] <= pos["sl"] if s > 0 else b["high"] >= pos["sl"]
                        if back:
                            close_pos(i, pos["sl"], "equilibre")
        d = pt.date()
        if d != day:
            day, per_day = d, 0
        if pos or pend or per_day >= fvg.MAX_TRADES:
            continue
        if not fvg.in_session(pt + dt.timedelta(minutes=14)):
            continue
        bias = bias_at(b["time"] + 900)
        if bias == 0:
            continue
        k = bisect.bisect_left(d1t, b["time"] - b["time"] % 86400)
        adr = fvg.adr14(d1[max(0, k - 14):k])
        f = fvg.find_fvg(m15[i - 119:i + 1], bias, adr, used)
        if not f:
            continue
        key, side, lo, hi = f
        entry = hi if side > 0 else lo
        if (b["close"] - entry) * side <= 0.1:
            continue
        used.add(key)
        per_day += 1
        pend = {"side": side, "entry": entry, "exp": i + 8}
    if pos:
        close_pos(n - 1, m15[-1]["close"], "fin donnees")
    return trades

def stats(tr, sl_usd):
    if not tr:
        return {"sl": sl_usd, "trades": 0}
    pn = [t["pnl"] for t in tr]
    wins = [x for x in pn if x > 0]
    loss = [x for x in pn if x <= 0]
    cum = peak = dd = 0.0
    for x in pn:
        cum += x
        peak = max(peak, cum)
        dd = max(dd, peak - cum)
    by_m = {}
    for t in tr:
        m = dt.datetime.utcfromtimestamp(t["close"]).strftime("%Y-%m")
        by_m[m] = round(by_m.get(m, 0) + t["R"], 1)
    return {"sl": sl_usd, "trades": len(tr), "winrate_pct": round(100 * len(wins) / len(tr), 1),
            "total_R": round(sum(t["R"] for t in tr), 1), "avg_R": round(sum(t["R"] for t in tr) / len(tr), 3),
            "profit_factor": round(sum(wins) / -sum(loss), 2) if loss and sum(loss) < 0 else None,
            "max_drawdown_R": round(dd / sl_usd, 1), "R_par_mois": by_m}

def to_list(a):
    if a is None:
        return []
    return [{"time": int(x["time"]), "open": float(x["open"]), "high": float(x["high"]),
             "low": float(x["low"]), "close": float(x["close"])} for x in a]

def main():
    import MetaTrader5 as mt5
    PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    ok = False
    for i in range(4):
        ok = mt5.initialize(path=PATH, login=int(os.environ["MT5_LOGIN"]), password=os.environ["MT5_PASSWORD"],
                            server=os.environ["MT5_SERVER"], timeout=120000)
        if ok:
            break
        log(f"tentative {i+1} echec: {mt5.last_error()}")
        mt5.shutdown()
        time.sleep(20)
    if not ok:
        log("connexion impossible")
        sys.exit(1)
    sym = os.environ.get("FVG_SYMBOL", "XAUUSD")
    if not mt5.symbol_info(sym):
        sym = next((s.name for s in mt5.symbols_get() or [] if s.name.upper().startswith(sym.upper())), None)
    if not sym:
        log("symbole introuvable")
        sys.exit(1)
    mt5.symbol_select(sym, True)
    time.sleep(5)
    m15 = to_list(mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 80000))
    h1 = to_list(mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_H1, 0, 20000))
    d1 = to_list(mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_D1, 0, 3000))
    mt5.shutdown()
    m15, h1 = m15[:-1], h1[:-1]
    log(f"{sym}: M15 {len(m15)} bougies, H1 {len(h1)}, D1 {len(d1)}")
    if len(m15) < 500:
        log("pas assez de donnees")
        sys.exit(1)
    log(f"periode {ptime(m15[0]['time']):%Y-%m-%d} -> {ptime(m15[-1]['time']):%Y-%m-%d}")
    res = []
    for sl in (5.0, 10.0, 15.0):
        tr = simulate(sl, m15, h1, d1)
        st = stats(tr, sl)
        res.append(st)
        log(json.dumps(st))
        if sl == 5.0:
            with open("out/trades_sl5.json", "w") as f:
                json.dump(tr, f)
    with open("out/backtest.json", "w") as f:
        json.dump(res, f, indent=1)

if __name__ == "__main__":
    main()
