import os, sys, time
import MetaTrader5 as mt5

LOGIN = int(os.environ["MT5_LOGIN"])
PASSWORD = os.environ["MT5_PASSWORD"]
SERVER = os.environ["MT5_SERVER"]
SYMBOL = os.environ.get("SYMBOL", "BTCUSD")
MINUTES = int(os.environ.get("MINUTES", "5"))
LOT, FAST, SLOW = 0.01, 9, 21
SL_PCT, TP_PCT = 0.005, 0.01
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

def cross():
    r = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 1, 100)
    if r is None or len(r) < 60:
        return 0, 0
    c = [x["close"] for x in r]
    f1, s1 = ema(c, FAST), ema(c, SLOW)
    f0, s0 = ema(c[:-1], FAST), ema(c[:-1], SLOW)
    t = int(r[-1]["time"])
    if f0 <= s0 and f1 > s1:
        return 1, t
    if f0 >= s0 and f1 < s1:
        return -1, t
    return 0, t

def trade(side):
    tick = mt5.symbol_info_tick(SYMBOL)
    price = tick.ask if side > 0 else tick.bid
    req = {
        "action": mt5.TRADE_ACTION_DEAL, "symbol": SYMBOL, "volume": LOT,
        "type": mt5.ORDER_TYPE_BUY if side > 0 else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": round(price * (1 - side * SL_PCT), mt5.symbol_info(SYMBOL).digits),
        "tp": round(price * (1 + side * TP_PCT), mt5.symbol_info(SYMBOL).digits),
        "deviation": 20, "magic": 2026, "comment": "ART_EURO demo",
        "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC,
    }
    res = mt5.order_send(req)
    log(f"ordre {'BUY' if side > 0 else 'SELL'} @ {price} -> {res.retcode if res else mt5.last_error()}")

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
log(f"connecte demo {acc.login}, solde {acc.balance}, symbole {SYMBOL}")
if not mt5.symbol_select(SYMBOL, True):
    log(f"symbole introuvable: {SYMBOL}")
    log("symboles BTC: " + ", ".join(s.name for s in (mt5.symbols_get("*BTC*") or [])))
    mt5.shutdown()
    sys.exit(1)
last, end = 0, time.time() + MINUTES * 60
while time.time() < end:
    side, t = cross()
    if side and t != last and not mt5.positions_get(symbol=SYMBOL):
        trade(side)
        last = t
    time.sleep(20)
log(f"fin, solde {mt5.account_info().balance}")
mt5.shutdown()
