"""CSP solver: each feedback clue is translated into constraints on
positions/letters (via OR-Tools CP-SAT, consistent with the CP approach used
for Sudoku), then the solver is asked for a satisfying word compatible with
the list of remaining candidates. An 'explored node' = number of branches
explored by CP-SAT (often 0, constraint propagation is enough)."""

from __future__ import annotations

import random

from ortools.sat.python import cp_model

from ..core import NodeCounter, SolverOutput
from .game import get_feedback, is_win
from .instances import MAX_ATTEMPTS

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def _pick_word_matching_constraints(
    candidates: list[str], length: int, counter: NodeCounter
) -> str | None:
    """Model 'which word of `candidates` to choose' as a CSP: one variable
    per position (index in the alphabet), constrained to match one of the
    remaining words (table constraint / allowed_assignments)."""
    if not candidates:
        return None

    model = cp_model.CpModel()
    position_vars = [model.new_int_var(0, 25, f"pos_{i}") for i in range(length)]
    tuples = [[ALPHABET.index(c) for c in word] for word in candidates]
    model.add_allowed_assignments(position_vars, tuples)

    solver = cp_model.CpSolver()
    solver.parameters.random_seed = 0
    status = solver.solve(model)
    counter.increment(int(solver.num_branches))
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    return "".join(ALPHABET[solver.value(v)] for v in position_vars)


def solve_csp(instance: tuple[str, list[str]], counter: NodeCounter, seed: int = 0) -> SolverOutput:
    target, all_words = instance
    length = len(target)
    rng = random.Random(seed)
    candidates = list(all_words)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # limit the constraint table size to stay fast on large candidate
        # pools (representative random sample)
        pool = candidates if len(candidates) <= 500 else rng.sample(candidates, 500)
        guess = _pick_word_matching_constraints(pool, length, counter)
        if guess is None:
            break
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
