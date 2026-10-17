import os, sys, time
import MetaTrader5 as mt5
import report

LOGIN = int(os.environ["MT5_LOGIN"])
PASSWORD = os.environ["MT5_PASSWORD"]
SERVER = os.environ["MT5_SERVER"]
MINUTES = int(os.environ.get("MINUTES", "5"))
CATS = [c.strip().lower() for c in os.environ.get("CATEGORIES", "Forex,Metals,Crypto,Indices").split(",") if c.strip()]
ACTIVE = [s.strip() for s in os.environ.get("STRATEGIES", "booster,ema").split(",") if s.strip()]
MAX_SYMBOLS = int(os.environ.get("MAX_SYMBOLS", "80"))
MAX_POS = int(os.environ.get("MAX_POS", "5"))
TF_MAP = {"M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15}
TF_B = TF_MAP[os.environ.get("BOOSTER_TF", "M5")]
EMA_FAST, EMA_SLOW, RSI_LEN, ADX_LEN, ADX_TH, ATR_LEN = 3, 8, 5, 14, 15.0, 14
STOP_DD = 0.05
MAGICS = {"booster": 2027, "ema": 2026}
PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
os.makedirs("out", exist_ok=True)

def log(m):
    line = time.strftime("%H:%M:%S ") + m
    print(line, flush=True)
    report.add_log(line)
    with open("out/bot.log", "a") as f:
        f.write(line + "\n")

def ema_series(vals, n):
    k = 2 / (n + 1)
    out, e = [], vals[0]
    for x in vals:
        e = x * k + e * (1 - k)
        out.append(e)
    return out

def true_ranges(r):
    return [max(r[i]["high"] - r[i]["low"], abs(r[i]["high"] - r[i-1]["close"]), abs(r[i]["low"] - r[i-1]["close"])) for i in range(1, len(r))]

def atr_rma(r, n=14):
    trs = true_ranges(r)
    a = sum(trs[:n]) / n
    for x in trs[n:]:
        a = (a * (n - 1) + x) / n
    return a

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

NONE = (0, 0, 0, 0, 0)
seen = {}

def new_bar(name, tf):
    cur = mt5.copy_rates_from_pos(name, tf, 0, 1)
    if cur is None or len(cur) == 0:
        return False
    t = int(cur[0]["time"])
    if seen.get((name, tf)) == t:
        return False
    seen[(name, tf)] = t
    return True

def sig_booster(name):
    if not new_bar(name, TF_B):
        return NONE
    r = mt5.copy_rates_from_pos(name, TF_B, 1, 300)
    if r is None or len(r) < 100:
        return NONE
    c = [x["close"] for x in r]
    ef, es, rs = ema_series(c, EMA_FAST), ema_series(c, EMA_SLOW), rsi_series(c, RSI_LEN)
    ad = adx_list(r, ADX_LEN)
    if len(ad) < 3:
        return NONE
    a = atr_rma(r, ATR_LEN)
    t = int(r[-1]["time"])

    def bull(i):
        ok = ad[i] >= ADX_TH or ad[i] > ad[i-1]
        return ef[i] > es[i] and c[i] > ef[i] and rs[i] > 50 and rs[i] > rs[i-1] and ok

    def bear(i):
        ok = ad[i] >= ADX_TH or ad[i] > ad[i-1]
        return ef[i] < es[i] and c[i] < ef[i] and rs[i] < 50 and rs[i] < rs[i-1] and ok

    if bull(-1) and not bull(-2):
        return 1, t, a, 1.2, 2.0
    if bear(-1) and not bear(-2):
        return -1, t, a, 1.2, 2.0
    return NONE

def sig_ema(name):
    if not new_bar(name, mt5.TIMEFRAME_M15):
        return NONE
    r = mt5.copy_rates_from_pos(name, mt5.TIMEFRAME_M15, 1, 100)
    if r is None or len(r) < 60:
        return NONE
    c = [x["close"] for x in r]
    f, s = ema_series(c, 9), ema_series(c, 21)
    t, a = int(r[-1]["time"]), atr_rma(r)
    if f[-2] <= s[-2] and f[-1] > s[-1]:
        return 1, t, a, 1.5, 3.0
    if f[-2] >= s[-2] and f[-1] < s[-1]:
        return -1, t, a, 1.5, 3.0
    return NONE

STRATS = {"booster": sig_booster, "ema": sig_ema}

def filling(info):
    if info.filling_mode & 1:
        return mt5.ORDER_FILLING_FOK
    if info.filling_mode & 2:
        return mt5.ORDER_FILLING_IOC
    return mt5.ORDER_FILLING_RETURN

def trade(name, side, a, slm, tpm, eq, strat):
    info = mt5.symbol_info(name)
    tick = mt5.symbol_info_tick(name)
    price = tick.ask if side > 0 else tick.bid
    typ = mt5.ORDER_TYPE_BUY if side > 0 else mt5.ORDER_TYPE_SELL
    margin = mt5.order_calc_margin(typ, name, info.volume_min, price)
    if margin is None or margin > eq * 0.10:
        log(f"{name}: ignore (marge trop elevee)")
        return False
    mind = info.trade_stops_level * info.point * 1.1
    d, dt = max(a * slm, mind), max(a * tpm, mind)
    req = {
        "action": mt5.TRADE_ACTION_DEAL, "symbol": name, "volume": info.volume_min,
        "type": typ, "price": price,
        "sl": round(price - side * d, info.digits), "tp": round(price + side * dt, info.digits),
        "deviation": 20, "magic": MAGICS[strat], "comment": "ART_EURO " + strat,
        "type_time": mt5.ORDER_TIME_GTC, "type_filling": filling(info),
    }
    res = mt5.order_send(req)
    code = res.retcode if res else mt5.last_error()
    log(f"[{strat}] {'BUY' if side > 0 else 'SELL'} {name} @ {price} -> {code}")
    return bool(res) and res.retcode == mt5.TRADE_RETCODE_DONE

ok = False
for i in range(4):
    ok = mt5.initialize(path=PATH, login=LOGIN, password=PASSWORD, server=SERVER, timeout=120000)
    if ok:
        break
    log(f"tentative {i+1} echec: {mt5.last_error()}")
    mt5.shutdown()
    time.sleep(20)
if not ok:
    log(f"connexion impossible: {mt5.last_error()}")
    sys.exit(1)
acc = mt5.account_info()
if acc.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
    log("compte non demo, arret")
    mt5.shutdown()
    sys.exit(1)
start_eq = acc.equity
log(f"connecte demo {acc.login}, solde {acc.balance}, strategies {ACTIVE}, categories {CATS}")

names = []
for s in mt5.symbols_get() or []:
    p = (s.path or "").lower()
    if s.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL and (not CATS or any(c in p for c in CATS)):
        names.append(s.name)
names = names[:MAX_SYMBOLS]
for n in names:
    mt5.symbol_select(n, True)
log(f"{len(names)} actifs negociables surveilles")
report.send(0, len(names), MINUTES, ACTIVE, MAGICS)

last, end, tick_log = {}, time.time() + MINUTES * 60, 0
while time.time() < end:
    ticks = {n: mt5.symbol_info_tick(n) for n in names}
    ref = max((t.time for t in ticks.values() if t), default=0)
    opened = [n for n, t in ticks.items() if t and ref - t.time < 300]
    eq = mt5.account_info().equity
    held = {p.symbol for p in (mt5.positions_get() or []) if p.magic in MAGICS.values()}
    if time.time() - tick_log > 60:
        log(f"{len(opened)}/{len(names)} actifs ouverts, {len(held)} positions, equity {eq}")
        tick_log = time.time()
        report.send(len(opened), len(names), MINUTES, ACTIVE, MAGICS)
    if eq < start_eq * (1 - STOP_DD):
        log("perte maximale atteinte, plus d'ordres")
        break
    for n in opened:
        for st in ACTIVE:
            if n in held or len(held) >= MAX_POS:
                break
            side, t, a, slm, tpm = STRATS[st](n)
            if side and last.get((n, st)) != t and a > 0:
                last[(n, st)] = t
                if trade(n, side, a, slm, tpm, eq, st):
                    held.add(n)
    time.sleep(10)
log(f"fin, solde {mt5.account_info().balance}")
report.send(len(opened), len(names), MINUTES, ACTIVE, MAGICS, finished=True)
mt5.shutdown()
