"""Strategie FVG (imbalances) pour ART_EURO : biais H1 (BOS), entree limit sur retest d'un FVG M15."""
import os
import time
import datetime as dt

SYMBOL = os.environ.get("FVG_SYMBOL", "XAUUSD")
MAGIC = 2028
RISK_PCT = 0.01          # 1 % de l'equity par trade
SL_USD = 5.0             # stop fixe en dollars de prix
TP1_USD = 5.0            # TP1 : on ferme 50 %
BE_PLUS = 0.10           # stop deplace a l'entree + 0,10 $
MIN_FVG_ADR = 0.03       # FVG >= 3 % de l'ADR14 D1
MAX_SPREAD = 0.40
MAX_TRADES = 5           # ordres par jour
KILL = -0.03             # arret du jour a -3 %
H_OPEN, H_CLOSE = 9, 22  # heure de Paris
PENDING_SECONDS = 2 * 3600
DRY = os.environ.get("FVG_DRY_RUN", "0") == "1"

S = {"day": None, "day_eq": 0.0, "trades": 0, "used": set(), "tp1": set(),
     "placed": {}, "killed": False, "bar": 0, "sym": None, "warned": False}


def _last_sunday(y, m):
    first_next = dt.datetime(y + 1, 1, 1) if m == 12 else dt.datetime(y, m + 1, 1)
    d = first_next - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def paris(ts=None):
    u = dt.datetime.utcfromtimestamp(time.time() if ts is None else ts)
    a = _last_sunday(u.year, 3).replace(hour=1)
    b = _last_sunday(u.year, 10).replace(hour=1)
    return u + dt.timedelta(hours=2 if a <= u < b else 1)


def in_session(p):
    return p.weekday() < 5 and H_OPEN <= p.hour < H_CLOSE


def bias_from(r):
    fh = fl = None
    fh_used = fl_used = False
    bias = 0
    for i in range(len(r)):
        if i >= 4:
            k = i - 2
            if all(r[k]["high"] > r[j]["high"] for j in (k - 2, k - 1, k + 1, k + 2)):
                fh, fh_used = r[k]["high"], False
            if all(r[k]["low"] < r[j]["low"] for j in (k - 2, k - 1, k + 1, k + 2)):
                fl, fl_used = r[k]["low"], False
        c = r[i]["close"]
        if fh is not None and not fh_used and c > fh:
            bias, fh_used = 1, True
        if fl is not None and not fl_used and c < fl:
            bias, fl_used = -1, True
    return bias


def adr14(d):
    h = list(d)[-14:]
    if len(h) < 5:
        return 0.0
    return sum(x["high"] - x["low"] for x in h) / len(h)


def find_fvg(r, bias, adr, used, look=40):
    n = len(r)
    for i in range(n - 1, max(1, n - look), -1):
        lo_b, hi_b = r[i - 2]["high"], r[i]["low"]
        hi_s, lo_s = r[i - 2]["low"], r[i]["high"]
        if bias > 0 and hi_b > lo_b:
            side, lo, hi = 1, lo_b, hi_b
        elif bias < 0 and hi_s > lo_s:
            side, lo, hi = -1, lo_s, hi_s
        else:
            continue
        key = int(r[i]["time"])
        if key in used or hi - lo < MIN_FVG_ADR * adr:
            continue
        later = [r[j]["close"] for j in range(i + 1, n)]
        if side > 0 and any(c < lo for c in later):
            continue
        if side < 0 and any(c > hi for c in later):
            continue
        return key, side, lo, hi
    return None


def last_swing(r, side):
    for k in range(len(r) - 3, 1, -1):
        if side > 0 and all(r[k]["low"] < r[j]["low"] for j in (k - 2, k - 1, k + 1, k + 2)):
            return r[k]["low"]
        if side < 0 and all(r[k]["high"] > r[j]["high"] for j in (k - 2, k - 1, k + 1, k + 2)):
            return r[k]["high"]
    return None


def lot_size(info, eq):
    per_lot = SL_USD / info.trade_tick_size * info.trade_tick_value
    v = eq * RISK_PCT / per_lot if per_lot > 0 else info.volume_min
    step = info.volume_step
    v = int(v / step + 1e-9) * step
    return round(max(info.volume_min, min(info.volume_max, v)), 8)


def _fill(mt5, info):
    if info.filling_mode & 1:
        return mt5.ORDER_FILLING_FOK
    if info.filling_mode & 2:
        return mt5.ORDER_FILLING_IOC
    return mt5.ORDER_FILLING_RETURN


def _close(mt5, log, info, pos, vol, why):
    tick = mt5.symbol_info_tick(pos.symbol)
    buy = pos.type == mt5.POSITION_TYPE_BUY
    req = {"action": mt5.TRADE_ACTION_DEAL, "symbol": pos.symbol, "volume": vol,
           "type": mt5.ORDER_TYPE_SELL if buy else mt5.ORDER_TYPE_BUY, "position": pos.ticket,
           "price": tick.bid if buy else tick.ask, "deviation": 20, "magic": MAGIC,
           "comment": "ART_EURO fvg", "type_time": mt5.ORDER_TIME_GTC, "type_filling": _fill(mt5, info)}
    res = mt5.order_send(req)
    log(f"[fvg] fermeture {vol} ({why}) -> {res.retcode if res else mt5.last_error()}")


def _remove_pending(mt5, log, o, why):
    res = mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": o.ticket})
    S["placed"].pop(o.ticket, None)
    log(f"[fvg] ordre limit annule ({why}) -> {res.retcode if res else mt5.last_error()}")


def _mine(mt5, sym):
    pos = [p for p in (mt5.positions_get(symbol=sym) or []) if p.magic == MAGIC]
    ords = [o for o in (mt5.orders_get(symbol=sym) or []) if o.magic == MAGIC]
    return pos, ords


def _manage(mt5, log, sym, info, new_bar):
    pos, _ = _mine(mt5, sym)
    for p in pos:
        side = 1 if p.type == mt5.POSITION_TYPE_BUY else -1
        tick = mt5.symbol_info_tick(sym)
        price = tick.bid if side > 0 else tick.ask
        dist = (price - p.price_open) * side
        mind = info.trade_stops_level * info.point * 1.1
        if p.ticket not in S["tp1"] and dist >= TP1_USD:
            half = int(p.volume / 2 / info.volume_step + 1e-9) * info.volume_step
            if half >= info.volume_min and p.volume - half >= info.volume_min:
                _close(mt5, log, info, p, round(half, 8), "TP1 50%")
            new_sl = round(p.price_open + side * BE_PLUS, info.digits)
            if (price - new_sl) * side > mind:
                res = mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "symbol": sym,
                                      "position": p.ticket, "sl": new_sl, "tp": p.tp})
                log(f"[fvg] stop a l'equilibre {new_sl} -> {res.retcode if res else mt5.last_error()}")
            S["tp1"].add(p.ticket)
        elif p.ticket in S["tp1"] and new_bar:
            r = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 1, 80)
            sw = last_swing(r, side) if r is not None and len(r) > 10 else None
            if sw is not None:
                sw = round(sw, info.digits)
                better = p.sl == 0 or (sw - p.sl) * side > 0
                if better and (price - sw) * side > mind:
                    res = mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "symbol": sym,
                                          "position": p.ticket, "sl": sw, "tp": p.tp})
                    log(f"[fvg] trailing swing M15 -> {sw} ({res.retcode if res else mt5.last_error()})")


def _flatten(mt5, log, sym, info, why):
    pos, ords = _mine(mt5, sym)
    for o in ords:
        _remove_pending(mt5, log, o, why)
    for p in pos:
        _close(mt5, log, info, p, p.volume, why)


def step(mt5, log, eq):
    try:
        _step(mt5, log, eq)
    except Exception as e:
        log(f"[fvg] erreur: {e!r}")


def _resolve(mt5, log):
    if S["sym"] is not None:
        return S["sym"]
    name = None
    if mt5.symbol_info(SYMBOL):
        name = SYMBOL
    else:
        for s in mt5.symbols_get() or []:
            if s.name.upper().startswith(SYMBOL.upper()):
                name = s.name
                break
    if name:
        mt5.symbol_select(name, True)
        log(f"[fvg] symbole {name}, mode {'SIMULATION' if DRY else 'reel demo'}")
    else:
        log(f"[fvg] symbole introuvable: {SYMBOL}")
    S["sym"] = name or False
    return S["sym"]


def _step(mt5, log, eq):
    sym = _resolve(mt5, log)
    if not sym:
        return
    info = mt5.symbol_info(sym)
    p = paris()
    day = p.date()
    if S["day"] != day:
        S.update(day=day, day_eq=eq, trades=0, killed=False)
        log(f"[fvg] nouveau jour {day}, equity de depart {eq}")

    cur = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 1)
    new_bar = False
    if cur is not None and len(cur) and int(cur[0]["time"]) != S["bar"]:
        S["bar"], new_bar = int(cur[0]["time"]), True

    if not S["killed"] and eq <= S["day_eq"] * (1 + KILL):
        S["killed"] = True
        log("[fvg] kill switch -3 % : arret jusqu'a demain")
        _flatten(mt5, log, sym, info, "kill switch")
    if not in_session(p):
        _flatten(mt5, log, sym, info, "hors session")
        return

    _manage(mt5, log, sym, info, new_bar)
    pos, ords = _mine(mt5, sym)
    for o in ords:
        t0 = S["placed"].setdefault(o.ticket, time.time())
        if time.time() - t0 > PENDING_SECONDS:
            _remove_pending(mt5, log, o, "expire")
    if S["killed"] or not new_bar:
        return

    h1 = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_H1, 1, 300)
    if h1 is None or len(h1) < 30:
        return
    bias = bias_from(h1)
    pos, ords = _mine(mt5, sym)
    for o in ords:
        want = 1 if o.type == mt5.ORDER_TYPE_BUY_LIMIT else -1
        if want != bias:
            _remove_pending(mt5, log, o, "biais change")
    pos, ords = _mine(mt5, sym)
    if pos or ords or bias == 0 or S["trades"] >= MAX_TRADES:
        return

    d1 = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_D1, 1, 20)
    m15 = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 1, 120)
    if d1 is None or m15 is None or len(m15) < 50:
        return
    adr = adr14(d1)
    f = find_fvg(m15, bias, adr, S["used"])
    if not f:
        return
    key, side, lo, hi = f
    tick = mt5.symbol_info_tick(sym)
    if tick.ask - tick.bid > MAX_SPREAD:
        log(f"[fvg] spread trop grand {tick.ask - tick.bid:.2f}")
        return
    entry = round(hi if side > 0 else lo, info.digits)
    mind = info.trade_stops_level * info.point * 1.1
    if (tick.ask - entry if side > 0 else entry - tick.bid) <= mind:
        return
    sl = round(entry - side * max(SL_USD, mind), info.digits)
    vol = lot_size(info, eq)
    typ = mt5.ORDER_TYPE_BUY_LIMIT if side > 0 else mt5.ORDER_TYPE_SELL_LIMIT
    margin = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY if side > 0 else mt5.ORDER_TYPE_SELL, sym, vol, entry)
    if margin is None or margin > eq * 0.25:
        log("[fvg] ignore (marge trop elevee)")
        return
    S["used"].add(key)
    txt = f"{'BUY' if side > 0 else 'SELL'} LIMIT {sym} {vol} @ {entry} sl {sl} (FVG {lo:.2f}-{hi:.2f}, ADR {adr:.1f})"
    if DRY:
        log("[fvg] SIMULATION " + txt)
        return
    req = {"action": mt5.TRADE_ACTION_PENDING, "symbol": sym, "volume": vol, "type": typ,
           "price": entry, "sl": sl, "tp": 0.0, "deviation": 20, "magic": MAGIC,
           "comment": "ART_EURO fvg", "type_time": mt5.ORDER_TIME_GTC,
           "type_filling": mt5.ORDER_FILLING_RETURN}
    res = mt5.order_send(req)
    ok = bool(res) and res.retcode in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_PLACED)
    log(f"[fvg] {txt} -> {res.retcode if res else mt5.last_error()}")
    if ok:
        S["trades"] += 1
        S["placed"][res.order] = time.time()
