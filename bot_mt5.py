import os, sys, time
import MetaTrader5 as mt5
import breakout
import report

LOGIN = int(os.environ["MT5_LOGIN"])
PASSWORD = os.environ["MT5_PASSWORD"]
SERVER = os.environ["MT5_SERVER"]
MINUTES = int(os.environ.get("MINUTES", "5"))
CATS = ["metals"]
ACTIVE = ["brk"]
MAX_SYMBOLS = 80
MAX_POS = 1
STOP_DD = 0.05
MAGICS = {"brk": 2029}
PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
os.makedirs("out", exist_ok=True)

def log(m):
    line = time.strftime("%H:%M:%S ") + m
    print(line, flush=True)
    report.add_log(line)
    with open("out/bot.log", "a") as f:
        f.write(line + "\n")

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

def algo_ok():
    ti = mt5.terminal_info()
    return bool(ti and ti.trade_allowed and not ti.tradeapi_disabled)

def ensure_algo():
    import subprocess, tempfile
    if algo_ok():
        log("trading automatique autorise")
        return
    log("trading automatique desactive dans MT5 : relance du terminal avec l'autorisation")
    mt5.shutdown()
    try:
        subprocess.run(["taskkill", "/F", "/IM", "terminal64.exe"], capture_output=True)
    except Exception as e:
        log(f"arret du terminal impossible: {e!r}")
    time.sleep(5)
    cfg = os.path.join(tempfile.gettempdir(), "mt5_algo.ini")
    with open(cfg, "w", encoding="utf-8") as f:
        f.write(f"[Common]\nLogin={LOGIN}\nPassword={PASSWORD}\nServer={SERVER}\n[Experts]\nEnabled=1\nAllowLiveTrading=1\nAllowDllImport=0\n")
    subprocess.Popen([PATH, "/config:" + cfg])
    time.sleep(60)
    up = False
    for _ in range(3):
        up = mt5.initialize(path=PATH, login=LOGIN, password=PASSWORD, server=SERVER, timeout=120000)
        if up:
            break
        time.sleep(15)
    try:
        os.remove(cfg)
    except OSError:
        pass
    if not up:
        log(f"reconnexion impossible: {mt5.last_error()}")
        sys.exit(1)
    ti = mt5.terminal_info()
    log(f"apres relance : trade_allowed={ti.trade_allowed if ti else None}, tradeapi_disabled={ti.tradeapi_disabled if ti else None}")

RM = set(MAGICS.values())

def deals_all():
    return mt5.history_deals_get(0, int(time.time()) + 172800) or []

def robot_pnl():
    real = 0.0
    for d in deals_all():
        if d.magic in RM and d.ticket not in base_deals:
            real += d.profit + d.commission + d.swap + getattr(d, "fee", 0.0)
    flo = sum(p.profit + p.swap for p in (mt5.positions_get() or []) if p.magic in RM)
    return real + flo

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
base_deals = {d.ticket for d in deals_all()}
chk = 0.0
log(f"connecte demo {acc.login}, solde {acc.balance}, strategies {ACTIVE}, categories {CATS}")

ensure_algo()
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
tick_seen = {}
while time.time() < end:
    ticks = {n: mt5.symbol_info_tick(n) for n in names}
    wall = time.time()
    for n, t in ticks.items():
        if not t:
            continue
        if n not in tick_seen:
            tick_seen[n] = [t.time_msc, 0.0]
        elif tick_seen[n][0] != t.time_msc:
            tick_seen[n] = [t.time_msc, wall]
    opened = [n for n in names if n in tick_seen and wall - tick_seen[n][1] < 300]
    eq = mt5.account_info().equity
    held = {p.symbol for p in (mt5.positions_get() or []) if p.magic in MAGICS.values()}
    if time.time() - tick_log > 60:
        log(f"{len(opened)}/{len(names)} actifs ouverts, {len(held)} positions, equity {eq}")
        tick_log = time.time()
        report.send(len(opened), len(names), MINUTES, ACTIVE, MAGICS)
    if time.time() - chk > 20:
        chk = time.time()
        rp = robot_pnl()
        if rp < -start_eq * STOP_DD:
            log(f"perte maximale du robot atteinte ({rp:.2f}), arret")
            break
    if "brk" in ACTIVE:
        breakout.step(mt5, log, eq)
    time.sleep(10)
log(f"fin, solde {mt5.account_info().balance}")
report.send(len(opened), len(names), MINUTES, ACTIVE, MAGICS, finished=True)
mt5.shutdown()
