# EURO — Mémoire de liquidité (recherche uniquement)

Ce module teste une idée de signal sur des bougies historiques OHLC. Il ne se connecte pas à MetaTrader, n'envoie aucun ordre et ne garantit aucun rendement.

## Fichiers

- `strategy_memory_liquidity.py` : détection d'un balayage d'un ancien plus haut/plus bas suivi d'une clôture de réintégration.
- `backtest_memory_liquidity.py` : simulation historique simple à partir d'un CSV.

## Format du CSV

Un fichier CSV avec au minimum les colonnes suivantes, dans cet ordre chronologique (ancien vers récent) :

```csv
time,open,high,low,close,spread
2026-01-01 10:00:00,2650.10,2651.20,2649.80,2650.90,0.20
```

Les prix doivent correspondre exactement au symbole et au courtier testés. La colonne `spread` est facultative et doit être exprimée en unités de prix, pas en points. Utiliser des données XAUUSD M1 réelles et suffisamment longues ; éviter les exemples fictifs pour conclure sur la stratégie.

## Exécution avec Python

Place les deux scripts et le CSV dans le même dossier, puis exécute :

```bash
python backtest_memory_liquidity.py XAUUSD_M1.csv --out rapport.json
```

Le risque simulé par défaut est de 0,25 % par trade. Pour tester un autre risque (maximum autorisé par le script : 1 %) :

```bash
python backtest_memory_liquidity.py XAUUSD_M1.csv --risk 0.0025 --out rapport.json
```

Le rapport affiche le nombre de trades, le taux de réussite, le résultat en R, le profit factor approximatif et le drawdown approximatif. Le détail des trades est enregistré dans le JSON.

## Limites importantes

- L'entrée est simulée à l'ouverture de la bougie suivant le signal.
- Si stop et objectif sont touchés dans la même bougie, le stop est considéré touché en premier.
- Les commissions, swaps, slippage, taille de contrat, marge et coût exact d'exécution ne sont pas simulés.
- Le filtre M15 n'est pas utilisé par le backtest actuel : le résultat mesure seulement la logique M1.
- Le calcul d'equity est une approximation, pas une simulation de compte MT5.
- Il faut séparer les données en période de développement et période de validation jamais utilisée pour ajuster les paramètres avant toute conclusion.
- Ne pas activer d'exécution réelle sur la base de ce rapport seul.
