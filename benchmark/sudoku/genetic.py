"""Algorithme genetique : chaque individu est une grille completee (blocs 3x3
remplis avec les chiffres 1-9 sans repetition), le fitness compte les
conflits restants sur les lignes/colonnes. Un 'noeud explore' = une evaluation
de fitness (un individu evalue).
"""

from __future__ import annotations

import random

from ..core import NodeCounter, SolverOutput
from .grid import SudokuGrid

POP_SIZE = 200
MAX_GENERATIONS = 2000
MUTATION_RATE = 0.15
STAGNATION_LIMIT = 100


def _fixed_mask(grid: SudokuGrid) -> list[list[bool]]:
    return [[grid.cells[r][c] != 0 for c in range(9)] for r in range(9)]


def _random_individual(grid: SudokuGrid, fixed: list[list[bool]], rng: random.Random) -> list[list[int]]:
    cells = [row[:] for row in grid.cells]
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            used = {
                cells[r][c]
                for r in range(box_row, box_row + 3)
                for c in range(box_col, box_col + 3)
                if fixed[r][c]
            }
            missing = [n for n in range(1, 10) if n not in used]
            rng.shuffle(missing)
            idx = 0
            for r in range(box_row, box_row + 3):
                for c in range(box_col, box_col + 3):
                    if not fixed[r][c]:
                        cells[r][c] = missing[idx]
                        idx += 1
    return cells


def _fitness(cells: list[list[int]]) -> int:
    conflicts = 0
    for r in range(9):
        conflicts += 9 - len(set(cells[r]))
    for c in range(9):
        conflicts += 9 - len({cells[r][c] for r in range(9)})
    return conflicts


def _crossover(a: list[list[int]], b: list[list[int]], rng: random.Random) -> list[list[int]]:
    child = []
    for box_row in range(0, 9, 3):
        parent = a if rng.random() < 0.5 else b
        child.extend(row[:] for row in parent[box_row : box_row + 3])
    return child


def _mutate(
    cells: list[list[int]], fixed: list[list[bool]], rng: random.Random
) -> None:
    """Mutation guidee : essaie plusieurs swaps dans un bloc et garde celui qui
    reduit le plus les conflits (hill-climbing local, courant dans les GA pour
    Sudoku car un swap aleatoire pur converge tres mal)."""
    box_row = rng.choice(range(0, 9, 3))
    box_col = rng.choice(range(0, 9, 3))
    free_cells = [
        (r, c)
        for r in range(box_row, box_row + 3)
        for c in range(box_col, box_col + 3)
        if not fixed[r][c]
    ]
    if len(free_cells) < 2:
        return

    base_fitness = _fitness(cells)
    best_swap = None
    best_delta = 0
    candidate_pairs = [rng.sample(free_cells, 2) for _ in range(min(6, len(free_cells)))]
    for (r1, c1), (r2, c2) in candidate_pairs:
        cells[r1][c1], cells[r2][c2] = cells[r2][c2], cells[r1][c1]
        delta = base_fitness - _fitness(cells)
        cells[r1][c1], cells[r2][c2] = cells[r2][c2], cells[r1][c1]
        if delta > best_delta:
            best_delta = delta
            best_swap = ((r1, c1), (r2, c2))

    if best_swap is None:
        (r1, c1), (r2, c2) = rng.sample(free_cells, 2)
    else:
        (r1, c1), (r2, c2) = best_swap
    cells[r1][c1], cells[r2][c2] = cells[r2][c2], cells[r1][c1]


def solve_genetic(grid: SudokuGrid, counter: NodeCounter, seed: int = 0) -> SolverOutput:
    rng = random.Random(seed)
    fixed = _fixed_mask(grid)
    population = [_random_individual(grid, fixed, rng) for _ in range(POP_SIZE)]

    best_cells = population[0]
    best_fitness = _fitness(best_cells)
    counter.increment(POP_SIZE)
    stagnant = 0

    for _generation in range(MAX_GENERATIONS):
        scored = sorted(population, key=_fitness)
        counter.increment(len(population))
        current_best = _fitness(scored[0])
        if current_best < best_fitness:
            best_cells, best_fitness = scored[0], current_best
            stagnant = 0
        else:
            stagnant += 1
        if best_fitness == 0:
            break

        if stagnant >= STAGNATION_LIMIT:
            # redemarrage partiel : garde l'elite, regenere le reste au hasard
            elite = scored[: POP_SIZE // 20]
            population = [row[:] for row in elite] + [
                _random_individual(grid, fixed, rng) for _ in range(POP_SIZE - len(elite))
            ]
            stagnant = 0
            continue

        elite = scored[: POP_SIZE // 10]
        next_gen = [row[:] for row in elite]
        while len(next_gen) < POP_SIZE:
            parent_a, parent_b = rng.sample(elite, 2) if len(elite) >= 2 else (scored[0], scored[1])
            child = _crossover(parent_a, parent_b, rng)
            if rng.random() < MUTATION_RATE:
                _mutate(child, fixed, rng)
                _mutate(child, fixed, rng)
            next_gen.append(child)
        population = next_gen

    result = SudokuGrid(best_cells)
    return SolverOutput(
        success=best_fitness == 0 and result.is_solved(),
        nodes_explored=counter.count,
        solution_quality=float(best_fitness),
    )
