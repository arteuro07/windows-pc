import sys

p = "bot_mt5.py"
s = open(p, encoding="utf-8").read()
if "import report" in s:
    print("Le robot est deja branche au panneau.")
    sys.exit(0)
edits = [
    ("import MetaTrader5 as mt5\n", "import MetaTrader5 as mt5\nimport report\n"),
    ("    print(line, flush=True)\n", "    print(line, flush=True)\n    report.add_log(line)\n"),
    ('log(f"{len(names)} actifs negociables surveilles")\n',
     'log(f"{len(names)} actifs negociables surveilles")\nreport.send(0, len(names), MINUTES, ACTIVE, MAGICS)\n'),
    ("        tick_log = time.time()\n",
     "        tick_log = time.time()\n        report.send(len(opened), len(names), MINUTES, ACTIVE, MAGICS)\n"),
    ('log(f"fin, solde {mt5.account_info().balance}")\n',
     'log(f"fin, solde {mt5.account_info().balance}")\nreport.send(len(opened), len(names), MINUTES, ACTIVE, MAGICS, finished=True)\n'),
]
for old, new in edits:
    if s.count(old) != 1:
        print("ECHEC : ligne attendue introuvable dans bot_mt5.py ->", old.strip())
        print("Rien n'a ete modifie. Envoie-moi ce message.")
        sys.exit(1)
    s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print("Robot branche au panneau.")
