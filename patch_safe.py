import sys

p = "bot_mt5.py"
s = open(p, encoding="utf-8").read()
if "robot_pnl" in s:
    print("Correction deja appliquee.")
    sys.exit(0)

FUNCS = '''def algo_ok():
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
        f.write(f"[Common]\\nLogin={LOGIN}\\nPassword={PASSWORD}\\nServer={SERVER}\\n[Experts]\\nEnabled=1\\nAllowLiveTrading=1\\nAllowDllImport=0\\n")
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

'''
edits = [
    ("ok = False\nfor i in range(4):\n", FUNCS + "ok = False\nfor i in range(4):\n"),
    ("start_eq = acc.equity\n", "start_eq = acc.equity\nbase_deals = {d.ticket for d in deals_all()}\nchk = 0.0\n"),
    ("names = []\nfor s in mt5.symbols_get() or []:\n", "ensure_algo()\nnames = []\nfor s in mt5.symbols_get() or []:\n"),
    ("    if eq < start_eq * (1 - STOP_DD):\n        log(\"perte maximale atteinte, plus d'ordres\")\n        break\n",
     "    if time.time() - chk > 20:\n        chk = time.time()\n        rp = robot_pnl()\n"
     "        if rp < -start_eq * STOP_DD:\n            log(f\"perte maximale du robot atteinte ({rp:.2f}), arret\")\n            break\n"),
]
for old, new in edits:
    if s.count(old) != 1:
        print("ECHEC : bloc attendu introuvable ->", old.strip().splitlines()[0])
        print("Rien n'a ete modifie. Envoie-moi ce message.")
        sys.exit(1)
    s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print("Correction appliquee : trading automatique force + arret de securite sur les seuls ordres du robot.")
