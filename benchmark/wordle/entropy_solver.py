"""Solveur par maximisation du gain d'information (entropie de Shannon), popularise
par la video 3Blue1Brown sur Wordle. Pour chaque mot candidat, on estime
l'entropie de la distribution des patterns de feedback qu'il produirait sur
l'ensemble des cibles possibles, et on joue le mot qui maximise cette entropie.
Un 'noeud explore' = un mot candidat evalue (calcul d'entropie)."""

from __future__ import annotations

import math
from collections import Counter

from ..core import NodeCounter, SolverOutput
from .game import get_feedback, is_win
from .instances import MAX_ATTEMPTS

# Le premier coup optimal ne depend que de la liste de mots (pas de la cible) :
# on le met en cache pour ne pas repeter le calcul le plus couteux a chaque instance.
_first_guess_cache: dict[tuple[str, ...], str] = {}


def _entropy(guess: str, candidates: list[str]) -> float:
    pattern_counts = Counter(get_feedback(guess, word) for word in candidates)
    total = len(candidates)
    return -sum(
        (count / total) * math.log2(count / total) for count in pattern_counts.values()
    )


def _best_guess(candidates: list[str], counter: NodeCounter) -> str:
    counter.increment(len(candidates))
    if len(candidates) <= 2:
        return candidates[0]
    return max(candidates, key=lambda guess: _entropy(guess, candidates))


def solve_entropy(instance: tuple[str, list[str]], counter: NodeCounter) -> SolverOutput:
    target, all_words = instance
    candidates = list(all_words)

    cache_key = tuple(all_words)
    first_guess = _first_guess_cache.get(cache_key)
    if first_guess is None:
        first_guess = _best_guess(candidates, counter)
        _first_guess_cache[cache_key] = first_guess
    else:
        counter.increment(len(candidates))

    guess = first_guess
    for attempt in range(1, MAX_ATTEMPTS + 1):
        feedback = get_feedback(guess, target)
        if is_win(feedback):
            return SolverOutput(
                success=True, nodes_explored=counter.count, solution_quality=float(attempt)
            )
        candidates = [w for w in candidates if get_feedback(guess, w) == feedback]
        if not candidates:
            break
        guess = _best_guess(candidates, counter)

    return SolverOutput(
        success=False, nodes_explored=counter.count, solution_quality=float(MAX_ATTEMPTS)
    )
