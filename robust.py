"""Robustesse du suivi de tendance EMA : voisinage des reglages, H4 et D1, annee par annee."""
import os, sys, time, json, datetime as dt
import research as rs
import backtest_strats as bs

log = bs.log
SYMS = rs.SYMS
GRID = [(f, s) for f in (30, 40, 50, 60, 80) for s in (150, 200, 250)]
EXITS = [(2, None, True), (3, None, True), (4, None, True), (1.5, 6, False)]

def year(t):
    return dt.datetime.utcfromtimestamp(t).year

def pf(R):
    w = sum(x for x in R if x > 0)
    l = -sum(x for x in R if x <= 0)
    return round(w / l, 2) if l > 0 else 99.0

def analyse(data, tfs=("H4", "D1")):
    out = {}
    atrs = {k: bs.atr_series(v, 14) for k, v in data.items()}
    for tf in tfs:
        rows = []
        for f, s in GRID:
            sg = {sym: rs.cross_sigs(data[(sym, tf)], f, s) for sym in SYMS if (sym, tf) in data}
            for slm, tpm, rev in EXITS:
                allt, per = [], {}
                for sym, g in sg.items():
                    t = rs.simulate(data[(sym, tf)], atrs[(sym, tf)], g, slm, tpm, rev, rs.SPREAD.get(sym, 0.0))
                    per[sym] = round(sum(x[1] for x in t), 1)
                    allt += t
                R = [x[1] for x in allt]
                yrs = {}
                for t, r in allt:
                    yrs[year(t)] = yrs.get(year(t), 0) + r
                rows.append({"cfg": f"ema{f}/{s} sl{slm} " + (f"tp{tpm}" if tpm else "rev"), "n": len(R), "R": round(sum(R), 1),
                             "pf": pf(R), "yrs": {y: round(v, 1) for y, v in sorted(yrs.items())},
                             "yrs_pos": sum(1 for v in yrs.values() if v > 0), "nyrs": len(yrs),
                             "syms_pos": sum(1 for v in per.values() if v > 0), "per": per})
        out[tf] = rows
    return out

def report(out):
    for tf, rows in out.items():
        good = [r for r in rows if r["pf"] > 1.05]
        log(f"== {tf} : {len(rows)} reglages voisins ; PF>1,05 : {len(good)} ; PF>1 : {sum(1 for r in rows if r['pf'] > 1)} ; PF median {sorted(r['pf'] for r in rows)[len(rows)//2]}")
        for ex in ("rev", "tp6"):
            sub = [r for r in rows if r["cfg"].endswith(ex)]
            if sub:
                log(f"   sortie {ex}: PF moyen {round(sum(r['pf'] for r in sub)/len(sub), 2)} ; annees positives en moyenne {round(sum(r['yrs_pos']/max(r['nyrs'],1) for r in sub)/len(sub)*100)} %")
        for r in sorted(rows, key=lambda r: -r["pf"])[:4]:
            log(f"   top {r['cfg']} n={r['n']} R={r['R']} pf={r['pf']} annees+ {r['yrs_pos']}/{r['nyrs']} marches+ {r['syms_pos']}/{len(SYMS)} {r['yrs']}")
        c = [r for r in rows if r["cfg"] == "ema50/200 sl3 rev"]
        if c:
            r = c[0]
            log(f"   CENTRE {r['cfg']} n={r['n']} R={r['R']} pf={r['pf']} annees {r['yrs']} par marche {r['per']}")

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
    data = {}
    for sym in SYMS:
        if not mt5.symbol_info(sym):
            log(f"{sym}: introuvable")
            continue
        mt5.symbol_select(sym, True)
        time.sleep(2)
        for tf, code, cnt in (("H4", mt5.TIMEFRAME_H4, 30000), ("D1", mt5.TIMEFRAME_D1, 5000)):
            r = bs.to_list(mt5.copy_rates_from_pos(sym, code, 0, cnt))[:-1]
            if len(r) > 300:
                data[(sym, tf)] = r
        log(f"{sym}: " + ", ".join(f"{tf} {len(data.get((sym, tf), []))} depuis {dt.datetime.utcfromtimestamp(data[(sym, tf)][0]['time']):%Y-%m}" for tf in ("H4", "D1") if (sym, tf) in data))
    mt5.shutdown()
    out = analyse(data)
    with open("out/robust.json", "w") as f:
        json.dump(out, f)
    report(out)

if __name__ == "__main__":
    main()
