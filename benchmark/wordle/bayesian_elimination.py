"""Elimination bayesienne simple : a chaque tour, on filtre les mots candidats
compatibles avec le feedback recu, et on choisit le prochain essai au hasard
(uniformement) parmi les candidats restants. Un 'noeud explore' = un mot
candidat evalue lors du filtrage."""

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
