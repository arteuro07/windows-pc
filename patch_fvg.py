import sys

def patch(path, edits, marker):
    s = open(path, encoding="utf-8").read()
    if marker in s:
        print(path, ": deja applique.")
        return True
    for old, new in edits:
        if s.count(old) != 1:
            print("ECHEC dans", path, "-> bloc introuvable:", old.strip().splitlines()[0])
            print("Rien n'a ete modifie dans ce fichier. Envoie-moi ce message.")
            return False
        s = s.replace(old, new)
    open(path, "w", encoding="utf-8").write(s)
    print(path, ": OK")
    return True

bot = [
    ("import MetaTrader5 as mt5\n", "import MetaTrader5 as mt5\nimport fvg\n"),
    ('MAGICS = {"booster": 2027, "ema": 2026}', 'MAGICS = {"booster": 2027, "ema": 2026, "fvg": 2028}'),
    ("        for st in ACTIVE:\n", "        for st in [x for x in ACTIVE if x in STRATS]:\n"),
    ('    time.sleep(10)\nlog(f"fin',
     '    if "fvg" in ACTIVE:\n        fvg.step(mt5, log, eq)\n    time.sleep(10)\nlog(f"fin'),
]
panel = [
    ("chipsBuild('c_str',[['booster','Scalping Booster'],['ema','EMA 9/21']],true,'str');",
     "chipsBuild('c_str',[['booster','Scalping Booster'],['ema','EMA 9/21'],['fvg','FVG Or']],true,'str');"),
    ("s==='booster'?'Booster':(s==='ema'?'EMA 9/21':s)",
     "s==='booster'?'Booster':(s==='ema'?'EMA 9/21':(s==='fvg'?'FVG Or':s))"),
    ('const STRS = ["booster", "ema"];', 'const STRS = ["booster", "ema", "fvg"];'),
]
a = patch("bot_mt5.py", bot, "import fvg")
b = patch("worker.js", panel, "FVG Or")
sys.exit(0 if a and b else 1)
