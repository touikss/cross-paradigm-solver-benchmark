"""Backtracking naif et variante MRV (Minimum Remaining Values).

Un 'noeud explore' correspond a une affectation (case, valeur) testee.
"""

from __future__ import annotations

from ..core import NodeCounter, SolverOutput
from .grid import SudokuGrid


def _solve(grid: SudokuGrid, counter: NodeCounter, use_mrv: bool) -> bool:
    empty = grid.find_empty_mrv() if use_mrv else grid.find_empty()
    if empty is None:
        return True
    row, col = empty
    for num in range(1, 10):
        counter.increment()
        if grid.is_valid_placement(row, col, num):
            grid.cells[row][col] = num
            if _solve(grid, counter, use_mrv):
                return True
            grid.cells[row][col] = 0
    return False


def solve_backtracking(grid: SudokuGrid, counter: NodeCounter) -> SolverOutput:
    work = grid.clone()
    success = _solve(work, counter, use_mrv=False)
    return SolverOutput(success=success and work.is_solved(), nodes_explored=counter.count)


def solve_backtracking_mrv(grid: SudokuGrid, counter: NodeCounter) -> SolverOutput:
    work = grid.clone()
    success = _solve(work, counter, use_mrv=True)
    return SolverOutput(success=success and work.is_solved(), nodes_explored=counter.count)
