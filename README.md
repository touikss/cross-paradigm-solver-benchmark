# Benchmark cross-paradigme de solveurs de jeux

Projet solo - cours *Intelligence Symbolique* (EPITA SCIA), sujet **L4** :
comparer systematiquement des paradigmes de resolution heterogenes (recherche
exacte, CSP/CP-SAT, SAT/SMT, metaheuristiques, recherche adversariale,
theorie de l'information) sur trois jeux : **Sudoku**, **Puissance 4**
(Connect Four) et **Wordle**.

Livrable principal : [`notebook.ipynb`](notebook.ipynb) (theorie + analyse +
visualisations + guide de selection de paradigme). Le code source des
solveurs est dans le paquet `benchmark/`, testable independamment du
notebook.

## Structure

```
benchmark/            # code source des solveurs (testable, importe par le notebook)
  core.py              # dataclass Metrics, orchestration (sequentielle et parallele)
  sudoku/              # 6 solveurs : backtracking(+MRV), dancing links, genetique, recuit simule, CP-SAT, SMT
  connect_four/        # 4 algorithmes : minimax, alpha-beta, MCTS, baseline
  wordle/              # 3 solveurs : elimination bayesienne, entropie, CSP
  run_all.py           # lance tous les benchmarks et sauvegarde results/*.csv
data/                 # instances de benchmark (grilles Sudoku, listes de mots Wordle)
results/              # CSV de resultats precalcules + figures exportees
tests/                # tests unitaires (pytest)
notebook.ipynb        # analyse et visualisations (livrable principal)
```

## Installation

```bash
uv sync
```

## Lancer les tests

```bash
uv run pytest
```

## Relancer les benchmarks

Les resultats sont deja precalcules dans `results/*.csv` (le notebook les
recharge directement, sans relancer les benchmarks a chaque execution). Pour
les regenerer :

```bash
uv run python -m benchmark.run_all
```

Le script distribue les instances sur plusieurs processus (une instance =
une tache independante) et reecrit le CSV de chaque jeu apres chaque
solveur termine, pour ne rien perdre en cas d'interruption. Comptez
quelques minutes au total (les metaheuristiques Sudoku et
minimax/alpha-beta a grande profondeur sur Puissance 4 sont les etapes les
plus lentes). Chaque instance est bornee a 2 minutes ; au-dela elle est
comptee en echec (timeout) plutot que de bloquer le benchmark.

## Executer le notebook

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebook.ipynb
# ou : uv run jupyter lab
```

## Sources des donnees

- **Sudoku** (`data/sudoku/`) : grilles Easy51 / top95 / hardest11, formats
  81-caracteres standard (0/`.` = case vide).
- **Wordle** (`data/wordle/`) : listes de mots anglais filtrees par longueur
  (5 a 8 lettres), extraites du corpus [`english-words`](https://pypi.org/project/english-words/)
  et figees dans des fichiers texte pour la reproductibilite (pas de
  telechargement a l'execution).
- **Connect Four** : aucune donnee externe, les instances (positions de
  depart par profondeur de recherche) sont generees en code.

## Perimetre et limites

Voir la section 5.4 du notebook pour la discussion detaillee. En resume :
6 paradigmes Sudoku sur 17 possibles (choix d'un sous-ensemble representatif
de chaque famille - recherche exacte, CSP/SAT, metaheuristique), Choco et
solveurs neuronaux/LLM non implementes (mentionnes en perspective).
