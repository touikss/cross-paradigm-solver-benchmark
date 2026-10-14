"""Solver maximizing information gain (Shannon entropy), popularized by the
3Blue1Brown video on Wordle. For each candidate word, we estimate the entropy
of the distribution of feedback patterns it would produce over the set of
possible targets, and play the word that maximizes this entropy.
An 'explored node' = one candidate word evaluated (entropy computation)."""

from __future__ import annotations

import math
from collections import Counter

from ..core import NodeCounter, SolverOutput
from .game import get_feedback, is_win
from .instances import MAX_ATTEMPTS

# The optimal first guess depends only on the word list (not on the target):
# cache it to avoid repeating the most expensive computation for every instance.
_first_guess_cache: dict[tuple[str, ...], str] = {}


def _entropy(guess: str, candidates: list[str]) -> float:
    pattern_counts = Counter(get_feedback(guess, word) for word in candidates)
    total = len(candidates)
    return -sum((count / total) * math.log2(count / total) for count in pattern_counts.values())


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
