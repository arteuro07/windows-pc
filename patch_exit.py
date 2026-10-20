p = "backtest_breakout.py"
s = open(p, encoding="utf-8").read()
if "SORTIE" in s:
    print("Deja applique.")
    raise SystemExit
a = "for ch in (18, 20, 22):"
b = "    return rows\n\ndef run_tf"
if s.count(a) != 1 or s.count(b) != 1:
    print("ECHEC : bloc introuvable. Rien modifie.")
    raise SystemExit(1)
s = s.replace(a, "for ch in (11, 12, 13, 14, 16, 18, 20, 22):")
s = s.replace(b, "    for r in rows:\n        if r['cfg'].startswith('fin7 ') and 'pct1.0' in r['cfg']:\n            log(f\"[{tag}] SORTIE {r['cfg']}: all={r['all']} test={r['test']}\")\n" + b)
open(p, "w", encoding="utf-8").write(s)
print("OK : sorties plus tot ajoutees au test.")
