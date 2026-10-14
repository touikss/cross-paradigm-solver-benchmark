"""Simple Bayesian elimination: at each turn, filter the candidate words
compatible with the received feedback, and pick the next guess at random
(uniformly) among the remaining candidates. An 'explored node' = one
candidate word evaluated during filtering."""

from __future__ import annotations

import random

from ..core import NodeCounter, SolverOutput
from .game import get_feedback, is_win
from .instances import MAX_ATTEMPTS


def solve_bayesian_elimination(
    instance: tuple[str, list[str]], counter: NodeCounter, seed: int = 0
) -> SolverOutput:
    target, all_words = instance
    rng = random.Random(seed)
    candidates = list(all_words)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        counter.increment(len(candidates))
        guess = rng.choice(candidates)
        feedback = get_feedback(guess, target)
        if is_win(feedback):
            return SolverOutput(
                success=True, nodes_explored=counter.count, solution_quality=float(attempt)
            )
        candidates = [w for w in candidates if get_feedback(guess, w) == feedback]
        if not candidates:
            break

    return SolverOutput(
        success=False, nodes_explored=counter.count, solution_quality=float(MAX_ATTEMPTS)
    )
