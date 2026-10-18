"""Recherche de strategie : choix sur la periode d'entrainement, verdict sur une periode jamais vue."""
import os, sys, time, json, datetime as dt
import numpy as np
import backtest_strats as bs

SYMS = [s.strip() for s in os.environ.get("SYMS", "XAUUSD,XAGUSD,EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,USDCHF").split(",") if s.strip()]
SPREAD = {"XAUUSD": 0.30, "XAGUSD": 0.03, "EURUSD": 0.00012, "GBPUSD": 0.00015, "USDJPY": 0.012,
          "AUDUSD": 0.00014, "USDCAD": 0.00016, "USDCHF": 0.00016}
SPLIT = int(dt.datetime(2025, 5, 1).replace(tzinfo=dt.timezone.utc).timestamp())
TFS = ["M15", "M30", "H1", "H4"]
EXITS = [(1.5, 3, False), (1.5, 6, False), (3, 3, False), (3, 6, False), (3, 12, False), (3, None, True), (2, None, True)]
log = bs.log

def cross_sigs(r, f, s):
    c = [x["close"] for x in r]
    ef, es = bs.ema_series(c, f), bs.ema_series(c, s)
    out = []
    for i in range(s + 1, len(r)):
        if ef[i-1] <= es[i-1] and ef[i] > es[i]:
            out.append((i, 1))
        elif ef[i-1] >= es[i-1] and ef[i] < es[i]:
            out.append((i, -1))
    return out

def donch_sigs(r, n):
    h = np.array([x["high"] for x in r]); l = np.array([x["low"] for x in r]); c = np.array([x["close"] for x in r])
    if len(r) <= n + 2:
        return []
    from numpy.lib.stride_tricks import sliding_window_view as swv
    hh = swv(h, n).max(axis=1)
    ll = swv(l, n).min(axis=1)
    up = np.zeros(len(r), bool); dn = np.zeros(len(r), bool)
    up[n:] = c[n:] > hh[:len(r) - n]
    dn[n:] = c[n:] < ll[:len(r) - n]
    out = []
    for i in range(n + 1, len(r)):
        if up[i] and not up[i-1]:
            out.append((i, 1))
        elif dn[i] and not dn[i-1]:
            out.append((i, -1))
    return out

def pull_sigs(r):
    c = [x["close"] for x in r]
    e50, e200, rs = bs.ema_series(c, 50), bs.ema_series(c, 200), bs.rsi_series(c, 14)
    out = []
    for i in range(210, len(r)):
        if c[i] > e200[i] and e50[i] > e200[i] and rs[i-1] < 40 <= rs[i]:
            out.append((i, 1))
        elif c[i] < e200[i] and e50[i] < e200[i] and rs[i-1] > 60 >= rs[i]:
            out.append((i, -1))
    return out

def boost_sigs(r, filt):
    s, _ = bs.signals_booster(r)
    if not filt:
        return s
    c = [x["close"] for x in r]
    e = bs.ema_series(c, 200)
    return [(i, d) for i, d in s if i > 200 and ((d > 0 and c[i] > e[i]) or (d < 0 and c[i] < e[i]))]

def simulate(r, atr, sigs, slm, tpm, rev, spread):
    n, trades, busy = len(r), [], -1
    for idx, (i, side) in enumerate(sigs):
        if i + 1 >= n or i < busy or atr[i] is None or atr[i] <= 0:
            continue
        a = atr[i]
        d = slm * a
        entry = r[i + 1]["open"]
        sl = entry - side * d
        tp = entry + side * tpm * a if tpm else None
        jb = None
        if rev:
            for jj in range(idx + 1, len(sigs)):
                if sigs[jj][1] != side:
                    jb = sigs[jj][0] + 1
                    break
        exit_p, k, by_rev = None, i + 1, False
        while k < n:
            b = r[k]
            if jb is not None and k == jb:
                exit_p, by_rev = b["open"], True
                break
            if (b["low"] <= sl) if side > 0 else (b["high"] >= sl):
                exit_p = min(b["open"], sl) if side > 0 else max(b["open"], sl)
                break
            if tp is not None and ((b["high"] >= tp) if side > 0 else (b["low"] <= tp)):
                exit_p = tp
                break
            k += 1
        if exit_p is None:
            exit_p, k = r[-1]["close"], n - 1
        trades.append((r[i + 1]["time"], ((exit_p - entry) * side - spread) / d))
        busy = k - 1 if by_rev else k
    return trades

def agg(tr):
    if not tr:
        return {"n": 0, "R": 0.0, "avg": 0.0, "pf": 0.0}
    R = [x[1] for x in tr]
    w = sum(x for x in R if x > 0)
    l = -sum(x for x in R if x <= 0)
    return {"n": len(R), "R": round(sum(R), 1), "avg": round(sum(R) / len(R), 3), "pf": round(w / l, 2) if l > 0 else 99.0}

def research(data):
    atrs = {k: bs.atr_series(v, 14) for k, v in data.items()}
    fams = []
    for tf in TFS:
        for f, s in ((9, 21), (20, 50), (20, 100), (50, 200)):
            fams.append((f"ema{f}/{s}", tf, lambda r, f=f, s=s: cross_sigs(r, f, s)))
        for n in (20, 50, 100):
            fams.append((f"donch{n}", tf, lambda r, n=n: donch_sigs(r, n)))
        fams.append(("pullback", tf, pull_sigs))
        for filt in (False, True):
            fams.append(("booster" + ("+f200" if filt else ""), tf, lambda r, filt=filt: boost_sigs(r, filt)))
    res = []
    for name, tf, fn in fams:
        sigs = {}
        for sym in SYMS:
            r = data.get((sym, tf))
            if r and len(r) > 500:
                sigs[sym] = fn(r)
        for slm, tpm, rev in EXITS:
            per, allt = {}, []
            for sym, sg in sigs.items():
                tr = simulate(data[(sym, tf)], atrs[(sym, tf)], sg, slm, tpm, rev, SPREAD.get(sym, 0.0))
                per[sym] = tr
                allt += tr
            tr_tr = [x for x in allt if x[0] < SPLIT]
            tr_te = [x for x in allt if x[0] >= SPLIT]
            pos = sum(1 for sym, t in per.items() if len([x for x in t if x[0] < SPLIT]) >= 20 and sum(x[1] for x in t if x[0] < SPLIT) > 0)
            res.append({"cfg": f"{name} {tf} sl{slm} " + (f"tp{tpm}" if tpm else "rev"), "train": agg(tr_tr), "test": agg(tr_te),
                        "pos_syms": pos, "gold_test": agg([x for x in per.get("XAUUSD", []) if x[0] >= SPLIT]),
                        "by_year": {y: round(sum(x[1] for x in allt if dt.datetime.utcfromtimestamp(x[0]).year == y), 1) for y in range(2023, 2027)}})
    return res

def report(res):
    cands = [c for c in res if c["train"]["n"] >= 200 and c["train"]["pf"] >= 1.15 and c["pos_syms"] >= 5]
    cands.sort(key=lambda c: -c["train"]["avg"])
    tp = [c for c in res if c["train"]["avg"] > 0]
    tpp = [c for c in tp if c["test"]["avg"] > 0]
    log(f"{len(res)} configurations testees")
    log(f"positives a l'entrainement : {len(tp)} ; encore positives sur la periode jamais vue : {len(tpp)}")
    log(f"candidates retenues (regles fixees a l'avance) : {len(cands)}")
    ok = [c for c in cands if c["test"]["avg"] > 0 and c["test"]["pf"] >= 1.1]
    log(f"candidates qui tiennent sur la periode jamais vue : {len(ok)}")
    for c in cands[:12]:
        log(f"{c['cfg']} | ENTRAINEMENT n={c['train']['n']} R={c['train']['R']} pf={c['train']['pf']} | JAMAIS VU n={c['test']['n']} R={c['test']['R']} pf={c['test']['pf']} | or jamais vu R={c['gold_test']['R']} | par an {c['by_year']}")
    if not cands:
        best = sorted(res, key=lambda c: -c["test"]["avg"])[:5]
        for c in best:
            log("meilleurs en test (non retenus) " + json.dumps(c))
    return cands, ok

def to_list(a):
    return bs.to_list(a)

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
    tfm = {"M15": (mt5.TIMEFRAME_M15, 80000), "M30": (mt5.TIMEFRAME_M30, 60000), "H1": (mt5.TIMEFRAME_H1, 30000), "H4": (mt5.TIMEFRAME_H4, 10000)}
    data = {}
    for sym in SYMS:
        if not mt5.symbol_info(sym):
            log(f"{sym}: introuvable")
            continue
        mt5.symbol_select(sym, True)
        time.sleep(2)
        for tf, (code, cnt) in tfm.items():
            r = to_list(mt5.copy_rates_from_pos(sym, code, 0, cnt))[:-1]
            if len(r) > 500:
                data[(sym, tf)] = r
        log(f"{sym}: " + ", ".join(f"{tf} {len(data.get((sym, tf), []))}" for tf in TFS))
    mt5.shutdown()
    t0 = time.time()
    res = research(data)
    log(f"calcul termine en {int(time.time() - t0)} s")
    with open("out/research.json", "w") as f:
        json.dump(res, f)
    report(res)

if __name__ == "__main__":
    main()
