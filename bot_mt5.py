import os, sys, time
import MetaTrader5 as mt5

LOGIN = int(os.environ["MT5_LOGIN"])
PASSWORD = os.environ["MT5_PASSWORD"]
SERVER = os.environ["MT5_SERVER"]
MINUTES = int(os.environ.get("MINUTES", "5"))
CATS = [c.strip().lower() for c in os.environ.get("CATEGORIES", "Forex,Metals,Crypto,Indices").split(",") if c.strip()]
MAX_SYMBOLS = int(os.environ.get("MAX_SYMBOLS", "80"))
MAX_POS = int(os.environ.get("MAX_POS", "5"))
FAST, SLOW, ATR_N = 9, 21, 14
SL_ATR, TP_ATR = 1.5, 3.0
STOP_DD = 0.05
MAGIC = 2026
PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
os.makedirs("out", exist_ok=True)

def log(m):
    line = time.strftime("%H:%M:%S ") + m
    print(line, flush=True)
    with open("out/bot.log", "a") as f:
        f.write(line + "\n")

def ema(vals, n):
    k = 2 / (n + 1)
    e = vals[0]
    for x in vals[1:]:
        e = x * k + e * (1 - k)
    return e

def atr(r, n=ATR_N):
    trs = [max(r[i]["high"] - r[i]["low"], abs(r[i]["high"] - r[i-1]["close"]), abs(r[i]["low"] - r[i-1]["close"])) for i in range(1, len(r))]
    return sum(trs[-n:]) / n

def signal(name):
    r = mt5.copy_rates_from_pos(name, mt5.TIMEFRAME_M15, 1, 100)
    if r is None or len(r) < 60:
        return 0, 0, 0
    c = [x["close"] for x in r]
    f1, s1 = ema(c, FAST), ema(c, SLOW)
    f0, s0 = ema(c[:-1], FAST), ema(c[:-1], SLOW)
    t, a = int(r[-1]["time"]), atr(r)
    if f0 <= s0 and f1 > s1:
        return 1, t, a
    if f0 >= s0 and f1 < s1:
        return -1, t, a
    return 0, t, a

def filling(info):
    if info.filling_mode & 1:
        return mt5.ORDER_FILLING_FOK
    if info.filling_mode & 2:
        return mt5.ORDER_FILLING_IOC
    return mt5.ORDER_FILLING_RETURN

def trade(name, side, a, eq):
    info = mt5.symbol_info(name)
    tick = mt5.symbol_info_tick(name)
    price = tick.ask if side > 0 else tick.bid
    typ = mt5.ORDER_TYPE_BUY if side > 0 else mt5.ORDER_TYPE_SELL
    margin = mt5.order_calc_margin(typ, name, info.volume_min, price)
    if margin is None or margin > eq * 0.10:
        log(f"{name}: ignore (marge trop elevee)")
        return False
    mind = info.trade_stops_level * info.point * 1.1
    d, dt = max(a * SL_ATR, mind), max(a * TP_ATR, mind)
    req = {
        "action": mt5.TRADE_ACTION_DEAL, "symbol": name, "volume": info.volume_min,
        "type": typ, "price": price,
        "sl": round(price - side * d, info.digits), "tp": round(price + side * dt, info.digits),
        "deviation": 20, "magic": MAGIC, "comment": "ART_EURO multi",
        "type_time": mt5.ORDER_TIME_GTC, "type_filling": filling(info),
    }
    res = mt5.order_send(req)
    code = res.retcode if res else mt5.last_error()
    log(f"ordre {'BUY' if side > 0 else 'SELL'} {name} @ {price} -> {code}")
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
log(f"connecte demo {acc.login}, solde {acc.balance}, categories {CATS}")

names = []
for s in mt5.symbols_get() or []:
    p = (s.path or "").lower()
    if s.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL and (not CATS or any(c in p for c in CATS)):
        names.append(s.name)
names = names[:MAX_SYMBOLS]
for n in names:
    mt5.symbol_select(n, True)
log(f"{len(names)} actifs negociables surveilles")

last, end = {}, time.time() + MINUTES * 60
while time.time() < end:
    ticks = {n: mt5.symbol_info_tick(n) for n in names}
    ref = max((t.time for t in ticks.values() if t), default=0)
    opened = [n for n, t in ticks.items() if t and ref - t.time < 300]
    eq = mt5.account_info().equity
    held = {p.symbol for p in (mt5.positions_get() or []) if p.magic == MAGIC}
    log(f"{len(opened)}/{len(names)} actifs ouverts, {len(held)} positions, equity {eq}")
    if eq < start_eq * (1 - STOP_DD):
        log("perte maximale atteinte, plus d'ordres")
        break
    for n in opened:
        if n in held or len(held) >= MAX_POS:
            continue
        side, t, a = signal(n)
        if side and last.get(n) != t and a > 0:
            if trade(n, side, a, eq):
                held.add(n)
            last[n] = t
    time.sleep(60)
log(f"fin, solde {mt5.account_info().balance}")
mt5.shutdown()
