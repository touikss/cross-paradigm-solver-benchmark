"""Simulated Annealing: same representation as the GA (filled blocks,
row/column conflicts as cost), but a single evolving state that moves by
swaps accepted under a Metropolis criterion. An 'explored node' = one
evaluation of the cost function (one swap tested).
"""

from __future__ import annotations

import math
import random

from ..core import NodeCounter, SolverOutput
from .genetic import _fitness, _fixed_mask, _random_individual
from .grid import SudokuGrid

INITIAL_TEMPERATURE = 2.0
COOLING_RATE = 0.99997
MIN_TEMPERATURE = 0.05
MAX_ITERATIONS = 300_000
STAGNATION_LIMIT = 20_000


def solve_simulated_annealing(
    grid: SudokuGrid, counter: NodeCounter, seed: int = 0
) -> SolverOutput:
    rng = random.Random(seed)
    fixed = _fixed_mask(grid)
    cells = _random_individual(grid, fixed, rng)
    cost = _fitness(cells)
    counter.increment()

    temperature = INITIAL_TEMPERATURE
    best_cells = [row[:] for row in cells]
    best_cost = cost

    boxes = [(br, bc) for br in range(0, 9, 3) for bc in range(0, 9, 3)]
    free_by_box = {
        (br, bc): [(r, c) for r in range(br, br + 3) for c in range(bc, bc + 3) if not fixed[r][c]]
        for br, bc in boxes
    }
    movable_boxes = [b for b in boxes if len(free_by_box[b]) >= 2]
    stagnant = 0

    for _iteration in range(MAX_ITERATIONS):
        if cost == 0:
            break
        box = rng.choice(movable_boxes)
        (r1, c1), (r2, c2) = rng.sample(free_by_box[box], 2)

        cells[r1][c1], cells[r2][c2] = cells[r2][c2], cells[r1][c1]
        new_cost = _fitness(cells)
        counter.increment()

        delta = new_cost - cost
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            cost = new_cost
            if cost < best_cost:
                best_cost = cost
                best_cells = [row[:] for row in cells]
                stagnant = 0
            else:
                stagnant += 1
        else:
            cells[r1][c1], cells[r2][c2] = cells[r2][c2], cells[r1][c1]
            stagnant += 1

        temperature = max(temperature * COOLING_RATE, MIN_TEMPERATURE)

        if stagnant >= STAGNATION_LIMIT:
            temperature = INITIAL_TEMPERATURE  # reheating
            stagnant = 0

    result = SudokuGrid(best_cells)
    return SolverOutput(
        success=best_cost == 0 and result.is_solved(),
        nodes_explored=counter.count,
        solution_quality=float(best_cost),
    )
