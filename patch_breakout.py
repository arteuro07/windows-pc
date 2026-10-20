import os, sys

def patch(path, edits, marker):
    if not os.path.exists(path):
        print("ECHEC :", path, "introuvable.")
        return False
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
    ("import fvg\n", "import fvg\nimport breakout\n"),
    ('"fvg": 2028}', '"fvg": 2028, "brk": 2029}'),
    ("        fvg.step(mt5, log, eq)\n",
     '        fvg.step(mt5, log, eq)\n    if "brk" in ACTIVE:\n        breakout.step(mt5, log, eq)\n'),
]
panel = [
    ("['fvg','FVG Or']],true,'str');", "['fvg','FVG Or'],['brk','Cassure Or']],true,'str');"),
    ("(s==='fvg'?'FVG Or':s)", "(s==='fvg'?'FVG Or':(s==='brk'?'Cassure Or':s))"),
    ('const STRS = ["booster", "ema", "fvg"];', 'const STRS = ["booster", "ema", "fvg", "brk"];'),
]
if not os.path.exists("breakout.py"):
    print("ECHEC : breakout.py introuvable. Rien n'a ete modifie.")
    sys.exit(1)
a = patch("bot_mt5.py", bot, "import breakout")
b = patch("worker.js", panel, "Cassure Or")
sys.exit(0 if a and b else 1)
