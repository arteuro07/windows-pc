"""Backtest 'cassure du range de nuit' sur l'or (MT5). Aucun ordre passe."""
import os, sys, time, json, datetime as dt
from collections import defaultdict

SYM = os.environ.get("SYM", "XAUUSD")
SPREAD = float(os.environ.get("BT_SPREAD", "0.25"))     # cout par trade en $ de prix
SPLIT = "2025-05-01"
RISK, MAXLEV = 0.01, 10.0
os.makedirs("out", exist_ok=True)

def log(m):
    line = time.strftime("%H:%M:%S ") + m
    print(line, flush=True)
    with open("out/backtest.log", "a") as f:
        f.write(line + "\n")

def to_list(a):
    if a is None:
        return []
    return [{"time": int(x["time"]), "open": float(x["open"]), "high": float(x["high"]),
             "low": float(x["low"]), "close": float(x["close"])} for x in a]

def by_day(bars):
    days = defaultdict(list)
    for b in bars:
        d = dt.datetime.utcfromtimestamp(b["time"])      # heure serveur du courtier
        days[d.date()].append((d.hour, b))
    return days

def simulate(days, rs, re_, ch, slmode, slpct, spread):
    out, first = [], True
    for day in sorted(days):
        if first:                    # 1er jour ignore (range peut etre incomplet)
            first = False
            continue
        bars = days[day]
        rng = [b for h, b in bars if rs <= h < re_]
        if not rng:
            continue
        H, L = max(b["high"] for b in rng), min(b["low"] for b in rng)
        if H <= L:
            continue
        trade, side, entry, sl, dist = None, 0, 0.0, 0.0, 0.0
        exit_p = None
        for h, b in bars:
            if h < re_:
                continue
            if side == 0:
                if h >= ch:
                    break
                lh, sh = b["high"] >= H, b["low"] <= L
                if not (lh or sh):
                    continue
                if lh and sh:
                    long_first = abs(b["open"] - H) <= abs(b["open"] - L)
                elif lh:
                    long_first = True
                else:
                    long_first = False
                side = 1 if long_first else -1
                entry = max(b["open"], H) if side > 0 else min(b["open"], L)
                if slmode == "pct":
                    sl = entry * (1 - side * slpct / 100.0)
                else:
                    sl = L if side > 0 else H
                dist = abs(entry - sl)
                if dist < entry * 0.0005:        # stop trop serre : trade ignore
                    side = 0
                    break
                # meme bougie : stop touche ? (pessimiste)
                if (side > 0 and b["low"] <= sl) or (side < 0 and b["high"] >= sl):
                    exit_p = sl
                    break
                continue
            # position ouverte
            if h >= ch:
                exit_p = b["open"]
                break
            if side > 0 and b["low"] <= sl:
                exit_p = min(b["open"], sl)
                break
            if side < 0 and b["high"] >= sl:
                exit_p = max(b["open"], sl)
                break
        if side == 0:
            continue
        if exit_p is None:
            exit_p = bars[-1][1]["close"]
        pnl = (exit_p - entry) * side - spread
        out.append({"day": day, "side": side, "pnl": pnl, "R": pnl / dist, "dist": dist, "entry": entry})
    return out

def stats(tr):
    if not tr:
        return None
    R = [t["R"] for t in tr]
    w, l = [x for x in R if x > 0], [x for x in R if x <= 0]
    eq, peak, dd = 1.0, 1.0, 0.0
    for t in tr:
        f = min(RISK / t["dist"], MAXLEV / t["entry"])      # onces par $ de capital
        eq *= max(1 + f * t["pnl"], 0.0)
        peak = max(peak, eq)
        dd = max(dd, 1 - eq / peak)
    return {"n": len(tr), "win%": round(100 * len(w) / len(R), 1), "avgR": round(sum(R) / len(R), 3),
            "totR": round(sum(R), 1), "PF": round(sum(w) / -sum(l), 2) if l and sum(l) < 0 else None,
            "ret%": round(100 * (eq - 1), 1), "maxDD%": round(100 * dd, 1)}

def split(tr):
    a = [t for t in tr if str(t["day"]) < SPLIT]
    b = [t for t in tr if str(t["day"]) >= SPLIT]
    return a, b

def per_year(tr):
    y = defaultdict(list)
    for t in tr:
        y[t["day"].year].append(t["R"])
    return {k: [len(v), round(sum(v), 1)] for k, v in sorted(y.items())}

def grid(days, tag):
    rows = []
    for re_ in (5, 6, 7, 8, 9):
        for ch in (11, 12, 13, 14, 16, 18, 20, 22):
            for slmode, slpct in (("pct", 0.5), ("pct", 1.0), ("pct", 1.5), ("range", 0)):
                tr = simulate(days, 0, re_, ch, slmode, slpct, SPREAD)
                a, b = split(tr)
                rows.append({"cfg": f"fin{re_} clot{ch} {slmode}{slpct if slmode == 'pct' else ''}",
                             "all": stats(tr), "train": stats(a), "test": stats(b)})
    pos_tr = sum(1 for r in rows if r["train"] and r["train"]["avgR"] > 0)
    pos_te = sum(1 for r in rows if r["test"] and r["test"]["avgR"] > 0)
    both = sum(1 for r in rows if r["train"] and r["test"] and r["train"]["avgR"] > 0 and r["test"]["avgR"] > 0)
    log(f"[{tag}] GRILLE {len(rows)} configs : avgR>0 en apprentissage {pos_tr}, en test {pos_te}, les deux {both}")
    for r in sorted(rows, key=lambda r: -(r["all"] or {"avgR": -9})["avgR"])[:5]:
        log(f"[{tag}] top  {r['cfg']}: all={r['all']} test={r['test']}")
    for r in sorted(rows, key=lambda r: (r["all"] or {"avgR": 9})["avgR"])[:2]:
        log(f"[{tag}] pire {r['cfg']}: all={r['all']}")
    for r in rows:
        if r['cfg'].startswith('fin7 ') and 'pct1.0' in r['cfg']:
            log(f"[{tag}] SORTIE {r['cfg']}: all={r['all']} test={r['test']}")
    return rows

def run_tf(bars, tag):
    days = by_day(bars)
    log(f"[{tag}] {len(bars)} bougies, du {dt.datetime.utcfromtimestamp(bars[0]['time']):%Y-%m-%d} "
        f"au {dt.datetime.utcfromtimestamp(bars[-1]['time']):%Y-%m-%d}, {len(days)} jours")
    res = {}
    for sp in (SPREAD, SPREAD * 2):
        tr = simulate(days, 0, 7, 20, "pct", 1.0, sp)
        a, b = split(tr)
        d = {"spread": sp, "all": stats(tr), "train": stats(a), "test": stats(b), "par_an": per_year(tr),
             "long": stats([t for t in tr if t["side"] > 0]), "short": stats([t for t in tr if t["side"] < 0])}
        log(f"[{tag}] DEFAUT 0-7h clot20h SL1% spread {sp}: " + json.dumps(d))
        res[f"defaut_spread{sp}"] = d
    res["grille"] = grid(days, tag)
    return res

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
    mt5.symbol_select(SYM, True)
    time.sleep(3)
    allres = {}
    for name, tf in (("M15", mt5.TIMEFRAME_M15), ("H1", mt5.TIMEFRAME_H1)):
        bars = to_list(mt5.copy_rates_from_pos(SYM, tf, 0, 80000))[:-1]
        if len(bars) < 2000:
            log(f"{name}: pas assez de donnees ({len(bars)})")
            continue
        allres[name] = run_tf(bars, name)
    mt5.shutdown()
    with open("out/backtest_breakout.json", "w") as f:
        json.dump(allres, f, indent=1, default=str)

if __name__ == "__main__":
    main()
