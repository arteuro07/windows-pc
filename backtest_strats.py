"""Backtest de Booster (M5) et EMA 9/21 (M15) sur l'historique MT5. Aucun ordre passe."""
import os, sys, time, json, datetime as dt

SYMS = [s.strip() for s in os.environ.get("SYMS", "XAUUSD,EURUSD,GBPUSD,USDJPY").split(",") if s.strip()]
SPREAD = {"XAUUSD": 0.25, "EURUSD": 0.00010, "GBPUSD": 0.00012, "USDJPY": 0.010}
os.makedirs("out", exist_ok=True)

def log(m):
    line = time.strftime("%H:%M:%S ") + m
    print(line, flush=True)
    with open("out/backtest.log", "a") as f:
        f.write(line + "\n")

def ema_series(vals, n):
    k = 2 / (n + 1)
    out, e = [], vals[0]
    for x in vals:
        e = x * k + e * (1 - k)
        out.append(e)
    return out

def atr_series(r, n=14):
    out = [None] * len(r)
    trs = [max(r[i]["high"] - r[i]["low"], abs(r[i]["high"] - r[i-1]["close"]), abs(r[i]["low"] - r[i-1]["close"])) for i in range(1, len(r))]
    if len(trs) < n:
        return out
    a = sum(trs[:n]) / n
    out[n] = a
    for j in range(n, len(trs)):
        a = (a * (n - 1) + trs[j]) / n
        out[j + 1] = a
    return out

def rsi_series(c, n):
    out = [50.0] * len(c)
    if len(c) <= n:
        return out
    g = [max(c[i] - c[i-1], 0) for i in range(1, len(c))]
    l = [max(c[i-1] - c[i], 0) for i in range(1, len(c))]
    ag, al = sum(g[:n]) / n, sum(l[:n]) / n
    out[n] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n, len(g)):
        ag = (ag * (n - 1) + g[i]) / n
        al = (al * (n - 1) + l[i]) / n
        out[i + 1] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out

def wilder(vals, n):
    s = sum(vals[:n])
    out = [s]
    for x in vals[n:]:
        s = s - s / n + x
        out.append(s)
    return out

def adx_list(r, n=14):
    h = [x["high"] for x in r]
    lo = [x["low"] for x in r]
    c = [x["close"] for x in r]
    tr, pdm, mdm = [], [], []
    for i in range(1, len(r)):
        up, dn = h[i] - h[i-1], lo[i-1] - lo[i]
        pdm.append(up if up > dn and up > 0 else 0.0)
        mdm.append(dn if dn > up and dn > 0 else 0.0)
        tr.append(max(h[i] - lo[i], abs(h[i] - c[i-1]), abs(lo[i] - c[i-1])))
    st, sp, sm = wilder(tr, n), wilder(pdm, n), wilder(mdm, n)
    dx = []
    for a, b, d in zip(st, sp, sm):
        if a == 0:
            dx.append(0.0)
            continue
        pi, mi = 100 * b / a, 100 * d / a
        dx.append(100 * abs(pi - mi) / (pi + mi) if pi + mi else 0.0)
    if len(dx) < n:
        return []
    v = sum(dx[:n]) / n
    out = [v]
    for x in dx[n:]:
        v = (v * (n - 1) + x) / n
        out.append(v)
    return out

def signals_booster(r, adx_th=15.0):
    n = len(r)
    c = [x["close"] for x in r]
    ef, es, rs = ema_series(c, 3), ema_series(c, 8), rsi_series(c, 5)
    ad = adx_list(r, 14)
    off = n - len(ad)
    def bull(i):
        j = i - off
        if j < 1:
            return False
        ok = ad[j] >= adx_th or ad[j] > ad[j-1]
        return ef[i] > es[i] and c[i] > ef[i] and rs[i] > 50 and rs[i] > rs[i-1] and ok
    def bear(i):
        j = i - off
        if j < 1:
            return False
        ok = ad[j] >= adx_th or ad[j] > ad[j-1]
        return ef[i] < es[i] and c[i] < ef[i] and rs[i] < 50 and rs[i] < rs[i-1] and ok
    out = []
    for i in range(off + 2, n):
        b, s = bull(i), bear(i)
        if b and not bull(i - 1):
            out.append((i, 1))
        elif s and not bear(i - 1):
            out.append((i, -1))
    return out, (1.2, 2.0)

def signals_ema(r):
    c = [x["close"] for x in r]
    f, s = ema_series(c, 9), ema_series(c, 21)
    out = []
    for i in range(60, len(r)):
        if f[i-1] <= s[i-1] and f[i] > s[i]:
            out.append((i, 1))
        elif f[i-1] >= s[i-1] and f[i] < s[i]:
            out.append((i, -1))
    return out, (1.5, 3.0)

def simulate(r, sigs, mults, spread):
    atr = atr_series(r, 14)
    slm, tpm = mults
    trades, busy_until = [], -1
    n = len(r)
    for i, side in sigs:
        if i + 1 >= n or i <= busy_until or atr[i] is None or atr[i] <= 0:
            continue
        a = atr[i]
        d, dt_ = a * slm, a * tpm
        entry = r[i + 1]["open"]
        sl, tp = entry - side * d, entry + side * dt_
        exit_p, k = None, i + 1
        while k < n:
            b = r[k]
            hit_sl = b["low"] <= sl if side > 0 else b["high"] >= sl
            hit_tp = b["high"] >= tp if side > 0 else b["low"] <= tp
            if hit_sl:
                exit_p = (min(b["open"], sl) if side > 0 else max(b["open"], sl))
                break
            if hit_tp:
                exit_p = tp
                break
            k += 1
        if exit_p is None:
            exit_p, k = r[-1]["close"], n - 1
        pnl = (exit_p - entry) * side - spread
        trades.append({"t": r[i + 1]["time"], "R": pnl / d, "cost_R": spread / d})
        busy_until = k
    return trades

def stats(tr):
    if not tr:
        return {"trades": 0}
    R = [t["R"] for t in tr]
    w = [x for x in R if x > 0]
    l = [x for x in R if x <= 0]
    cum = peak = dd = 0.0
    for x in R:
        cum += x
        peak = max(peak, cum)
        dd = max(dd, peak - cum)
    yr = {}
    for t in tr:
        y = str(dt.datetime.utcfromtimestamp(t["t"]).year)
        yr[y] = round(yr.get(y, 0) + t["R"], 1)
    return {"trades": len(tr), "winrate_pct": round(100 * len(w) / len(R), 1), "total_R": round(sum(R), 1),
            "avg_R": round(sum(R) / len(R), 3), "avg_cost_R": round(sum(t["cost_R"] for t in tr) / len(tr), 3),
            "profit_factor": round(sum(w) / -sum(l), 2) if l and sum(l) < 0 else None,
            "max_drawdown_R": round(dd, 1), "R_par_an": yr}

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
    allres, pool = {}, {"booster": [], "ema": []}
    for sym in SYMS:
        if not mt5.symbol_info(sym):
            log(f"{sym}: introuvable, ignore")
            continue
        mt5.symbol_select(sym, True)
        time.sleep(3)
        sp = SPREAD.get(sym, 0.0)
        for name, tf, fn in (("booster", mt5.TIMEFRAME_M5, signals_booster), ("ema", mt5.TIMEFRAME_M15, signals_ema)):
            r = to_list(mt5.copy_rates_from_pos(sym, tf, 0, 80000))[:-1]
            if len(r) < 1000:
                log(f"{sym} {name}: pas assez de donnees ({len(r)})")
                continue
            sigs, mults = fn(r)
            tr = simulate(r, sigs, mults, sp)
            st = stats(tr)
            st["bougies"] = len(r)
            st["debut"] = dt.datetime.utcfromtimestamp(r[0]["time"]).strftime("%Y-%m-%d")
            allres[f"{sym}/{name}"] = st
            pool[name] += tr
            log(f"{sym} {name}: " + json.dumps(st))
    mt5.shutdown()
    for name, tr in pool.items():
        st = stats(tr)
        allres[f"TOTAL/{name}"] = st
        log(f"TOTAL {name}: " + json.dumps(st))
    with open("out/backtest_strats.json", "w") as f:
        json.dump(allres, f, indent=1)

if __name__ == "__main__":
    main()
