import sys

p = "bot_mt5.py"
s = open(p, encoding="utf-8").read()
if "tick_seen" in s:
    print("Correction deja appliquee.")
    sys.exit(0)
edits = [
    ("last, end, tick_log = {}, time.time() + MINUTES * 60, 0\n",
     "last, end, tick_log = {}, time.time() + MINUTES * 60, 0\ntick_seen = {}\n"),
    ("    ref = max((t.time for t in ticks.values() if t), default=0)\n"
     "    opened = [n for n, t in ticks.items() if t and ref - t.time < 300]\n",
     "    wall = time.time()\n"
     "    for n, t in ticks.items():\n"
     "        if not t:\n"
     "            continue\n"
     "        if n not in tick_seen:\n"
     "            tick_seen[n] = [t.time_msc, 0.0]\n"
     "        elif tick_seen[n][0] != t.time_msc:\n"
     "            tick_seen[n] = [t.time_msc, wall]\n"
     "    opened = [n for n in names if n in tick_seen and wall - tick_seen[n][1] < 300]\n"),
]
for old, new in edits:
    if s.count(old) != 1:
        print("ECHEC : bloc attendu introuvable dans bot_mt5.py ->", old.strip().splitlines()[0])
        print("Rien n'a ete modifie. Envoie-moi ce message.")
        sys.exit(1)
    s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print("Correction appliquee : un actif est 'ouvert' seulement si son prix bouge vraiment.")
