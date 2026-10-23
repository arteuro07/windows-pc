"""Backtest 'Order Block / Supply Zone' (video olinvest.fx) sur l'or (MT5). Aucun ordre passe.

Logique (cote vente ; l'achat est teste en miroir, prix * -1) :
  1. Pivots confirmes (k bougies de chaque cote, aucun regard vers l'avenir).
  2. Cassure de structure (BOS) : une bougie CLOT sous le dernier creux pivot, apres un sommet pivot.
  3. Jambe : du sommet au creux L (le creux est connu quand un nouveau pivot bas est confirme apres la cassure).
  4. Zone d'entree, selon la variante :
       fib : ordre limite a L + f*R (f = 0.5 / 0.618 / 0.705), stop a L + 0.82*R   (zone OTE)
       ob  : ordre limite au bas du dernier order block (derniere bougie haussiere avant la cassure),
             stop au-dessus de l'order block ET du niveau 0.786 (comme la video)
       hvn : zone supply = noeud de volume (profil de volume des bougies, volume en ticks) autour du sommet,
             ordre limite au bas de la zone, stop au-dessus
     Cible = bas de la jambe (L). Un seul trade a la fois par sens.
  5. Execution prudente : stop avant cible si les deux dans la meme bougie ; ordre non execute si la
     meme bougie touche aussi la cible ; cout = spread par trade.
"""
import os, sys, time, json, datetime as dt
from collections import defaultdict

SYM = os.environ.get("SYM", "XAUUSD")
SPREAD = float(os.environ.get("BT_SPREAD", "0.25"))     # cout par trade en $ de prix
SPLIT = "2025-05-01"
RISK, MAXLEV = 0.01, 10.0
MIN_DIST = 0.0005          # stop minimum : 0,05 % du prix
os.makedirs("out", exist_ok=True)


def log(m):
    line = time.strftime("%H:%M:%S ") + m
    print(line, flush=True)
    with open("out/ob_backtest.log", "a") as f:
        f.write(line + "\n")


def mirror(bars):
    return [{"time": b["time"], "open": -b["open"], "high": -b["low"], "low": -b["high"],
             "close": -b["close"], "vol": b["vol"]} for b in bars]


def run_sell(B, k, mode, fib=0.618, maxage=100, maxhold=150, spread=SPREAD):
    n = len(B)
    O = [b["open"] for b in B]
    H = [b["high"] for b in B]
    Lw = [b["low"] for b in B]
    C = [b["close"] for b in B]
    V = [b["vol"] for b in B]
    T = [b["time"] for b in B]
    ph, pl = [], []                 # pivots confirmes (idx, prix)
    used_pl = -1
    st = None
    trades = []
    skipped = defaultdict(int)
    for t in range(2 * k, n):
        i = t - k
        if H[i] > max(H[i - k:i]) and H[i] >= max(H[i + 1:t + 1]):
            ph.append((i, H[i]))
        new_low = False
        if Lw[i] < min(Lw[i - k:i]) and Lw[i] <= min(Lw[i + 1:t + 1]):
            pl.append((i, Lw[i]))
            new_low = True

        # ---------- trade ouvert
        if st is not None and st["s"] == "trade":
            e, sl, tp = st["E"], st["SL"], st["TP"]
            ex = None
            if H[t] >= sl:
                ex = max(O[t], sl)
            elif Lw[t] <= tp:
                ex = tp
            elif t - st["fill"] >= maxhold:
                ex = C[t]
            if ex is not None:
                pnl = (e - ex) - spread
                trades.append({"t": T[st["fill"]], "day": dt.datetime.utcfromtimestamp(T[st["fill"]]).date(),
                               "pnl": pnl, "R": pnl / st["dist"], "dist": st["dist"], "entry": e,
                               "mode": mode})
                st = None
            continue

        # ---------- ordre en attente
        if st is not None and st["s"] == "order":
            e, sl, tp = st["E"], st["SL"], st["TP"]
            if H[t] > e:
                if Lw[t] <= tp and H[t] < sl:          # ambigu : on ne prend pas le trade
                    skipped["ambigu"] += 1
                    st = None
                    continue
                if H[t] >= sl:                         # rempli puis stop dans la meme bougie
                    pnl = (e - max(e, sl)) - spread
                    trades.append({"t": T[t], "day": dt.datetime.utcfromtimestamp(T[t]).date(), "pnl": pnl,
                                   "R": pnl / st["dist"], "dist": st["dist"], "entry": e, "mode": mode})
                    st = None
                    continue
                st = {"s": "trade", "E": e, "SL": sl, "TP": tp, "dist": st["dist"], "fill": t}
                continue
            if Lw[t] <= tp:
                skipped["jambe etendue"] += 1
                st = None
            elif t - st["created"] > maxage:
                skipped["expire"] += 1
                st = None
            continue

        # ---------- jambe en cours (cassure faite, on attend le creux)
        if st is not None and st["s"] == "leg":
            st["min"] = min(st["min"], Lw[t])
            if H[t] > st["top"]:
                skipped["nouveau sommet"] += 1
                st = None
                continue
            if new_low and i >= st["bos"]:
                top, L = st["top"], st["min"]
                R = top - L
                if R <= 0:
                    st = None
                    continue
                if mode == "fib":
                    E = L + fib * R
                    SL = L + 0.82 * R
                elif mode == "ob":
                    ob = st["ob"]
                    E = ob[0]
                    SL = max(ob[1] + 0.1 * (ob[1] - ob[0]), L + 0.82 * R)
                else:
                    z = st["hvn"]
                    if z is None:
                        skipped["pas de hvn"] += 1
                        st = None
                        continue
                    E = z[0]
                    SL = z[1] + 0.1 * (z[1] - z[0])
                dist = SL - E
                if mode != "fib" and E < L + 0.382 * R:
                    skipped["zone trop basse"] += 1
                    st = None
                    continue
                if dist < E * 0 + abs(E) * MIN_DIST or E <= C[t] or SL >= top + R * 0.5:
                    skipped["zone inutilisable"] += 1
                    st = None
                    continue
                st = {"s": "order", "E": E, "SL": SL, "TP": L, "dist": dist, "created": t}
            continue

        # ---------- recherche d'une cassure de structure
        if pl and ph and ph[-1][0] > pl[-1][0] and pl[-1][0] != used_pl and C[t] < pl[-1][1]:
            used_pl = pl[-1][0]
            pi = pl[-1][0]
            seg = H[pi:t + 1]
            top = max(seg)
            ti = pi + seg.index(top)
            ob = None
            for j in range(t - 1, ti - 1, -1):
                if C[j] > O[j]:
                    ob = (Lw[j], H[j])
                    break
            hvn = None
            if mode == "hvn":
                a = max(0, ti - 20)
                lo, hi = min(Lw[a:t + 1]), max(H[a:t + 1])
                if hi > lo:
                    nb = 24
                    step = (hi - lo) / nb
                    prof = [0.0] * nb
                    for j in range(a, t + 1):
                        b0 = min(nb - 1, int((Lw[j] - lo) / step))
                        b1 = min(nb - 1, int((H[j] - lo) / step))
                        share = V[j] / (b1 - b0 + 1)
                        for q in range(b0, b1 + 1):
                            prof[q] += share
                    poc = max(range(nb), key=lambda q: prof[q])
                    q0 = q1 = poc
                    while q0 > 0 and prof[q0 - 1] >= 0.6 * prof[poc]:
                        q0 -= 1
                    while q1 < nb - 1 and prof[q1 + 1] >= 0.6 * prof[poc]:
                        q1 += 1
                    hvn = (lo + q0 * step, lo + (q1 + 1) * step)
            if mode == "ob" and ob is None:
                skipped["pas d'order block"] += 1
                continue
            st = {"s": "leg", "bos": t, "top": top, "ob": ob, "hvn": hvn, "min": Lw[t]}
    return trades, dict(skipped)


def stats(tr):
    if not tr:
        return None
    R = [t["R"] for t in tr]
    w, l = [x for x in R if x > 0], [x for x in R if x <= 0]
    eq, peak, dd = 1.0, 1.0, 0.0
    for t in tr:
        f = min(RISK / t["dist"], MAXLEV / abs(t["entry"]))
        eq *= max(1 + f * t["pnl"], 0.0)
        peak = max(peak, eq)
        dd = max(dd, 1 - eq / peak)
    return {"n": len(tr), "win%": round(100 * len(w) / len(R), 1), "avgR": round(sum(R) / len(R), 3),
            "totR": round(sum(R), 1), "PF": round(sum(w) / -sum(l), 2) if l and sum(l) < 0 else None,
            "ret%": round(100 * (eq - 1), 1), "maxDD%": round(100 * dd, 1)}


def per_year(tr):
    y = defaultdict(list)
    for t in tr:
        y[t["day"].year].append(t["R"])
    return {k: [len(v), round(sum(v), 1)] for k, v in sorted(y.items())}


def evaluate(bars, tag, ks, spread):
    mir = mirror(bars)
    rows = []
    cfgs = [("fib", 0.5), ("fib", 0.618), ("fib", 0.705), ("ob", 0), ("hvn", 0)]
    for k in ks:
        for mode, f in cfgs:
            tr_s, sk_s = run_sell(bars, k, mode, f, spread=spread)
            tr_b, sk_b = run_sell(mir, k, mode, f, spread=spread)
            tr = sorted(tr_s + tr_b, key=lambda x: x["t"])
            for x in tr_b:
                x["side"] = 1
            for x in tr_s:
                x["side"] = -1
            a = [x for x in tr if str(x["day"]) < SPLIT]
            b = [x for x in tr if str(x["day"]) >= SPLIT]
            name = f"k{k} {mode}" + (f" {f}" if mode == "fib" else "")
            rows.append({"cfg": name, "all": stats(tr), "train": stats(a), "test": stats(b),
                         "par_an": per_year(tr), "vente": stats([x for x in tr if x["side"] < 0]),
                         "achat": stats([x for x in tr if x["side"] > 0]), "skipped": sk_s})
            log(f"[{tag}] sp{spread} {name}: all={rows[-1]['all']} test={rows[-1]['test']}")
    return rows


def summarize(res, tag):
    out = []
    for sp, rows in res.items():
        pos_tr = sum(1 for r in rows if r["train"] and r["train"]["avgR"] > 0)
        pos_te = sum(1 for r in rows if r["test"] and r["test"]["avgR"] > 0)
        both = sum(1 for r in rows if r["train"] and r["test"] and r["train"]["avgR"] > 0 and r["test"]["avgR"] > 0)
        out.append(f"[{tag}] {sp}: {len(rows)} configs, avgR>0 train {pos_tr}, test {pos_te}, les deux {both}")
        valid = [r for r in rows if r["train"]]
        if valid:
            best = max(valid, key=lambda r: r["train"]["avgR"])
            out.append(f"[{tag}] {sp}: MEILLEURE SUR L'APPRENTISSAGE = {best['cfg']} | train={best['train']} | "
                       f"TEST (jamais vu)={best['test']} | par an={best['par_an']}")
        for r in rows:
            a, t = r["all"], r["test"]
            out.append(f"[{tag}] {sp} {r['cfg']:<16} n={a['n'] if a else 0:<5} avgR={a['avgR'] if a else '-':<7} "
                       f"PF={a['PF'] if a else '-':<5} win%={a['win%'] if a else '-':<5} DD={a['maxDD%'] if a else '-':<5} "
                       f"| test avgR={t['avgR'] if t else '-'} PF={t['PF'] if t else '-'}")
    return out


def to_list(a):
    if a is None:
        return []
    names = a.dtype.names
    return [{"time": int(x["time"]), "open": float(x["open"]), "high": float(x["high"]), "low": float(x["low"]),
             "close": float(x["close"]), "vol": float(x["tick_volume"]) if "tick_volume" in names else 1.0}
            for x in a]


def run_all(data):
    allres, lines = {}, []
    for tag, (bars, ks) in data.items():
        log(f"[{tag}] {len(bars)} bougies, du {dt.datetime.utcfromtimestamp(bars[0]['time']):%Y-%m-%d} "
            f"au {dt.datetime.utcfromtimestamp(bars[-1]['time']):%Y-%m-%d}")
        res = {}
        for sp in (SPREAD, SPREAD * 2):
            res[f"spread{sp}"] = evaluate(bars, tag, ks, sp)
        allres[tag] = res
        lines += summarize(res, tag)
    with open("out/ob_results.json", "w") as f:
        json.dump(allres, f, indent=1, default=str)
    with open("out/ob_summary.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    for ln in lines:
        log(ln)


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
    data = {}
    for name, tf, ks in (("M15", mt5.TIMEFRAME_M15, (4, 6)), ("H1", mt5.TIMEFRAME_H1, (3, 5))):
        bars = to_list(mt5.copy_rates_from_pos(SYM, tf, 0, 80000))[:-1]
        if len(bars) < 2000:
            log(f"{name}: pas assez de donnees ({len(bars)})")
            continue
        data[name] = (bars, ks)
    mt5.shutdown()
    run_all(data)


if __name__ == "__main__":
    main()
