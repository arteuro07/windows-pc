"""Strategie 'Cassure Or' pour ART_EURO.

Range de nuit (00h-07h, heure du serveur du courtier) sur l'or. A 07h : ordres STOP au-dessus du haut
(achat) et sous le bas (vente), stop-loss a 1 % du prix d'entree, pas de objectif. Le premier ordre execute
annule l'autre. Un seul trade par jour. Tout est ferme a 18h (heure serveur).

Aucun etat n'est garde en memoire d'une session a l'autre : tout se relit dans MT5 (positions, ordres,
historique des deals du magic 2029). Le robot peut donc etre relance a tout moment.
"""
import os
import time
import datetime as dt

SYMBOL = os.environ.get("BRK_SYMBOL", "XAUUSD")
MAGIC = 2029
RISK_PCT = 0.005            # risque vise : 0,5 % de l'equity par trade
MAX_RISK_PCT = 0.02         # si le lot minimum depasse la cible, on accepte jusqu'a 2 %, sinon on ignore
SL_PCT = 0.01               # stop a 1 % du prix d'entree
MAX_LEV = 10.0              # exposition maximale : 10 x l'equity
RANGE_TO = 7                # le range est 00h -> 07h ; les ordres sont poses a partir de 07h
CLOSE_H = 18                # fermeture de tout a 18h
MIN_RANGE_BARS = 12         # bougies M15 minimum pour accepter le range
LATE_ENTRY_MIN = 60         # cassure deja faite : entree au marche permise jusqu'a 60 min apres 07h
RETRY_S = 60
MAX_TRIES = 5
DRY = os.environ.get("BRK_DRY_RUN", "0") == "1"

S = {"sym": None, "day": None, "tries": 0, "last_try": 0.0, "skip": None, "range_logged": None,
     "sl_try": {}, "offset_logged": False}


def server_ts(mt5, sym):
    t = mt5.symbol_info_tick(sym)
    return int(t.time) if t is not None and getattr(t, "time", 0) else None


def _fill(mt5, info):
    if info.filling_mode & 1:
        return mt5.ORDER_FILLING_FOK
    if info.filling_mode & 2:
        return mt5.ORDER_FILLING_IOC
    return mt5.ORDER_FILLING_RETURN


def _mine(mt5, sym):
    pos = [p for p in (mt5.positions_get(symbol=sym) or []) if p.magic == MAGIC]
    ords = [o for o in (mt5.orders_get(symbol=sym) or []) if o.magic == MAGIC]
    return pos, ords


def _close(mt5, log, info, pos, why):
    tick = mt5.symbol_info_tick(pos.symbol)
    buy = pos.type == mt5.POSITION_TYPE_BUY
    req = {"action": mt5.TRADE_ACTION_DEAL, "symbol": pos.symbol, "volume": pos.volume,
           "type": mt5.ORDER_TYPE_SELL if buy else mt5.ORDER_TYPE_BUY, "position": pos.ticket,
           "price": tick.bid if buy else tick.ask, "deviation": 30, "magic": MAGIC,
           "comment": "ART_EURO brk", "type_time": mt5.ORDER_TIME_GTC, "type_filling": _fill(mt5, info)}
    res = mt5.order_send(req)
    log(f"[brk] fermeture ({why}) -> {res.retcode if res else mt5.last_error()}")


def _remove(mt5, log, o, why):
    res = mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": o.ticket})
    log(f"[brk] ordre annule ({why}) -> {res.retcode if res else mt5.last_error()}")


def _flatten(mt5, log, info, pos, ords, why):
    for o in ords:
        _remove(mt5, log, o, why)
    for p in pos:
        _close(mt5, log, info, p, why)


def traded_today(mt5, day0):
    for d in mt5.history_deals_get(0, int(time.time()) + 172800) or []:
        if d.magic == MAGIC and d.time >= day0:
            return True
    return False


def lot_size(info, eq, price):
    dist = price * SL_PCT
    per_lot = dist / info.trade_tick_size * info.trade_tick_value
    if per_lot <= 0:
        return None
    step = info.volume_step
    cap = eq * MAX_LEV / (info.trade_contract_size * price)
    v = min(eq * RISK_PCT / per_lot, cap)
    v = int(v / step + 1e-9) * step
    if v < info.volume_min:
        if info.volume_min * per_lot > eq * MAX_RISK_PCT or info.volume_min > cap:
            return None
        v = info.volume_min
    return round(min(v, info.volume_max), 8), per_lot


def _fix_sl(mt5, log, info, p):
    """Comme la strategie d'origine : le stop est recale a 1 % du prix reellement obtenu."""
    side = 1 if p.type == mt5.POSITION_TYPE_BUY else -1
    want = round(p.price_open * (1 - side * SL_PCT), info.digits)
    if p.sl and abs(p.sl - want) <= 2 * info.trade_tick_size:
        return
    if S["sl_try"].get(p.ticket, 0) >= 3:
        return
    S["sl_try"][p.ticket] = S["sl_try"].get(p.ticket, 0) + 1
    res = mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "symbol": p.symbol, "position": p.ticket,
                          "sl": want, "tp": p.tp})
    log(f"[brk] stop recale a {want} (1 % du prix reel {p.price_open}) -> {res.retcode if res else mt5.last_error()}")


def _send_pending(mt5, log, info, typ, price, sl, vol, expiry, name):
    base = {"action": mt5.TRADE_ACTION_PENDING, "symbol": S["sym"], "volume": vol, "type": typ,
            "price": price, "sl": sl, "tp": 0.0, "deviation": 30, "magic": MAGIC, "comment": "ART_EURO brk"}
    variants = []
    for fill in (mt5.ORDER_FILLING_RETURN, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK):
        variants.append(dict(base, type_time=mt5.ORDER_TIME_SPECIFIED, expiration=expiry, type_filling=fill))
        variants.append(dict(base, type_time=mt5.ORDER_TIME_GTC, type_filling=fill))
    res = None
    for req in variants:
        res = mt5.order_send(req)
        if res and res.retcode in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_PLACED):
            log(f"[brk] {name} STOP {vol} @ {price} sl {sl} -> {res.retcode}")
            return True
        if res and res.retcode not in (10022, 10030):      # autre erreur : inutile d'insister
            break
    log(f"[brk] {name} STOP @ {price} refuse -> {res.retcode if res else mt5.last_error()}")
    return False


def _market(mt5, log, info, side, tick, eq):
    price = tick.ask if side > 0 else tick.bid
    lot = lot_size(info, eq, price)
    if not lot:
        log("[brk] lot minimum trop risque pour ce capital : jour ignore")
        return False
    vol, per_lot = lot
    sl = round(price * (1 - side * SL_PCT), info.digits)
    txt = f"{'BUY' if side > 0 else 'SELL'} MARCHE {vol} @ {price} sl {sl} (risque ~{vol * per_lot / eq * 100:.2f} %)"
    if DRY:
        log("[brk] SIMULATION " + txt)
        return True
    res = mt5.order_send({"action": mt5.TRADE_ACTION_DEAL, "symbol": S["sym"], "volume": vol,
                          "type": mt5.ORDER_TYPE_BUY if side > 0 else mt5.ORDER_TYPE_SELL, "price": price,
                          "sl": sl, "tp": 0.0, "deviation": 30, "magic": MAGIC, "comment": "ART_EURO brk",
                          "type_time": mt5.ORDER_TIME_GTC, "type_filling": _fill(mt5, info)})
    log(f"[brk] {txt} -> {res.retcode if res else mt5.last_error()}")
    return bool(res) and res.retcode == mt5.TRADE_RETCODE_DONE


def step(mt5, log, eq):
    try:
        _step(mt5, log, eq)
    except Exception as e:      # ne jamais faire tomber le robot
        log(f"[brk] erreur: {e!r}")


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
        log(f"[brk] symbole {name}, mode {'SIMULATION' if DRY else 'reel demo'}")
    else:
        log(f"[brk] symbole introuvable: {SYMBOL}")
    S["sym"] = name or False
    return S["sym"]


def _step(mt5, log, eq):
    sym = _resolve(mt5, log)
    if not sym:
        return
    info = mt5.symbol_info(sym)
    ts = server_ts(mt5, sym)
    if ts is None:
        return
    if not S["offset_logged"]:
        S["offset_logged"] = True
        log(f"[brk] heure serveur {dt.datetime.utcfromtimestamp(ts):%Y-%m-%d %H:%M} "
            f"(ecart avec UTC : {round((ts - time.time()) / 3600)} h)")
    d = dt.datetime.utcfromtimestamp(ts)
    day0 = ts - ts % 86400
    pos, ords = _mine(mt5, sym)

    # hors de la fenetre 07h-18h (ou week-end) : tout fermer
    if not (d.weekday() < 5 and RANGE_TO <= d.hour < CLOSE_H):
        if pos or ords:
            _flatten(mt5, log, info, pos, ords, f"hors fenetre 07h-{CLOSE_H}h")
        return

    # un seul trade par jour : l'autre ordre est annule des qu'un ordre est execute
    if pos:
        if ords:
            for o in ords:
                _remove(mt5, log, o, "l'autre cote est execute")
        if len(pos) > 1:
            pos.sort(key=lambda p: p.time)
            for p in pos[1:]:
                _close(mt5, log, info, p, "un seul trade par jour")
            pos = pos[:1]
        for p in pos:
            _fix_sl(mt5, log, info, p)
        return
    if ords:
        return          # ordres armes : on attend la cassure

    if S["day"] != day0:
        S.update(day=day0, tries=0, last_try=0.0)
    if S["skip"] == day0 or S["tries"] >= MAX_TRIES or time.time() - S["last_try"] < RETRY_S:
        return
    S["last_try"] = time.time()
    if traded_today(mt5, day0):
        S["skip"] = day0
        return

    r = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 300)
    if r is None or len(r) == 0:
        return
    bars = [x for x in r if day0 <= int(x["time"]) < day0 + RANGE_TO * 3600]
    if len(bars) < MIN_RANGE_BARS:
        log(f"[brk] range incomplet ({len(bars)} bougies) : jour ignore")
        S["skip"] = day0
        return
    hi = max(float(x["high"]) for x in bars)
    lo = min(float(x["low"]) for x in bars)
    if hi <= lo:
        S["skip"] = day0
        return
    if S["range_logged"] != day0:
        S["range_logged"] = day0
        log(f"[brk] range {d:%Y-%m-%d} : {lo} -> {hi} (largeur {(hi - lo) / lo * 100:.2f} %)")

    tick = mt5.symbol_info_tick(sym)
    mind = info.trade_stops_level * info.point * 1.1
    late = (ts - (day0 + RANGE_TO * 3600)) / 60.0
    broke = 1 if tick.ask >= hi else (-1 if tick.bid <= lo else 0)
    if broke:
        if late > LATE_ENTRY_MIN:
            log(f"[brk] cassure deja faite depuis plus de {LATE_ENTRY_MIN} min : jour ignore")
            S["skip"] = day0
            return
        if _market(mt5, log, info, broke, tick, eq):
            if DRY:
                S["skip"] = day0
        else:
            S["tries"] += 1
        return

    entry_b = round(max(hi, tick.ask + mind), info.digits)
    entry_s = round(min(lo, tick.bid - mind), info.digits)
    expiry = day0 + CLOSE_H * 3600
    placed = 0
    for side, entry, typ, name in ((1, entry_b, mt5.ORDER_TYPE_BUY_STOP, "BUY"),
                                   (-1, entry_s, mt5.ORDER_TYPE_SELL_STOP, "SELL")):
        lot = lot_size(info, eq, entry)
        if not lot:
            log("[brk] lot minimum trop risque pour ce capital : jour ignore")
            S["skip"] = day0
            return
        vol, per_lot = lot
        sl = round(entry * (1 - side * SL_PCT), info.digits)
        margin = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY if side > 0 else mt5.ORDER_TYPE_SELL, sym, vol, entry)
        if margin is None or margin > eq * 0.5:
            log("[brk] marge trop elevee : jour ignore")
            S["skip"] = day0
            return
        if DRY:
            log(f"[brk] SIMULATION {name} STOP {vol} @ {entry} sl {sl} (risque ~{vol * per_lot / eq * 100:.2f} %)")
            placed += 1
            continue
        if _send_pending(mt5, log, info, typ, entry, sl, vol, expiry, name):
            placed += 1
    if not placed:
        S["tries"] += 1
    elif DRY:
        S["skip"] = day0
