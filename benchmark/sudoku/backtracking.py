"""Backtracking naif et variante MRV (Minimum Remaining Values).

Un 'noeud explore' correspond a une affectation (case, valeur) testee. Un
budget de noeuds maximum evite l'explosion combinatoire du backtracking naif
sur certaines grilles adversariales (echec par depassement de budget = un
resultat empirique en soi, illustrant la limite du paradigme).
"""

from __future__ import annotations

from ..core import NodeCounter, SolverOutput
from .grid import SudokuGrid

DEFAULT_MAX_NODES = 2_000_000


class _NodeBudgetExceeded(Exception):
    pass


def _solve(grid: SudokuGrid, counter: NodeCounter, use_mrv: bool, max_nodes: int) -> bool:
    empty = grid.find_empty_mrv() if use_mrv else grid.find_empty()
    if empty is None:
        return True
    row, col = empty
    for num in range(1, 10):
        counter.increment()
        if counter.count > max_nodes:
            raise _NodeBudgetExceeded()
        if grid.is_valid_placement(row, col, num):
            grid.cells[row][col] = num
            if _solve(grid, counter, use_mrv, max_nodes):
                return True
            grid.cells[row][col] = 0
    return False


def _run(grid: SudokuGrid, counter: NodeCounter, use_mrv: bool, max_nodes: int) -> SolverOutput:
    work = grid.clone()
    try:
        success = _solve(work, counter, use_mrv, max_nodes)
    except _NodeBudgetExceeded:
        return SolverOutput(
            success=False, nodes_explored=counter.count, extra={"budget_exceeded": True}
        )
    return SolverOutput(success=success and work.is_solved(), nodes_explored=counter.count)


def solve_backtracking(
    grid: SudokuGrid, counter: NodeCounter, max_nodes: int = DEFAULT_MAX_NODES
) -> SolverOutput:
    return _run(grid, counter, use_mrv=False, max_nodes=max_nodes)


def solve_backtracking_mrv(
    grid: SudokuGrid, counter: NodeCounter, max_nodes: int = DEFAULT_MAX_NODES
) -> SolverOutput:
    return _run(grid, counter, use_mrv=True, max_nodes=max_nodes)
