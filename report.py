import os, json, urllib.request
from datetime import datetime, timedelta
import MetaTrader5 as mt5

URL = os.environ.get("PANEL_URL", "").rstrip("/")
KEY = os.environ.get("PANEL_KEY", "")
RUN = os.environ.get("GITHUB_RUN_ID", "local")
_log = []


def add_log(line):
    _log.append(line)
    del _log[:-60]


def send(opened, total, minutes, strategies, magics, finished=False):
    if not URL or not KEY:
        return
    try:
        a = mt5.account_info()
        by = {v: k for k, v in magics.items()}
        mine = set(magics.values())
        pos = [{"symbol": p.symbol, "side": "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL",
                "profit": round(p.profit, 2), "strat": by.get(p.magic, "?"), "volume": p.volume}
               for p in (mt5.positions_get() or []) if p.magic in mine]
        now = datetime.now()
        deals = []
        for d in mt5.history_deals_get(now - timedelta(days=2), now + timedelta(days=2)) or []:
            if d.magic in mine and d.entry == mt5.DEAL_ENTRY_OUT:
                deals.append({"ticket": d.ticket, "symbol": d.symbol, "strat": by.get(d.magic, "?"),
                              "side": "BUY" if d.type == mt5.DEAL_TYPE_SELL else "SELL",
                              "profit": round(d.profit + d.commission + d.swap, 2),
                              "time": d.time, "volume": d.volume, "price": d.price})
        body = {"run_id": RUN, "balance": a.balance, "equity": a.equity, "opened": opened, "total": total,
                "minutes": minutes, "strategies": ",".join(strategies), "positions": pos,
                "deals": deals[-100:], "log": list(_log), "finished": finished}
        req = urllib.request.Request(
            URL + "/api/report", data=json.dumps(body).encode(), method="POST",
            headers={"content-type": "application/json", "x-key": KEY, "user-agent": "art-euro-bot"})
        urllib.request.urlopen(req, timeout=15).read()
        _log.clear()
    except Exception as e:
        print("rapport echec:", e, flush=True)
