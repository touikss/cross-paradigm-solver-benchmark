"""Programmation par contraintes moderne via OR-Tools CP-SAT.

Un 'noeud explore' correspond au nombre de branches (decisions) explorees par
le solveur CP-SAT, recupere via les statistiques du solveur.
"""

from __future__ import annotations

from ortools.sat.python import cp_model

from ..core import NodeCounter, SolverOutput
from .grid import SudokuGrid


def solve_cp_sat(grid: SudokuGrid, counter: NodeCounter) -> SolverOutput:
    model = cp_model.CpModel()
    cells = [[model.new_int_var(1, 9, f"c_{r}_{c}") for c in range(9)] for r in range(9)]

    for r in range(9):
        model.add_all_different(cells[r])
    for c in range(9):
        model.add_all_different([cells[r][c] for r in range(9)])
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            model.add_all_different(
                cells[r][c]
                for r in range(box_row, box_row + 3)
                for c in range(box_col, box_col + 3)
            )
    for r in range(9):
        for c in range(9):
            if grid.cells[r][c] != 0:
                model.add(cells[r][c] == grid.cells[r][c])

    solver = cp_model.CpSolver()
    status = solver.solve(model)
    counter.increment(int(solver.num_branches))

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return SolverOutput(success=False, nodes_explored=counter.count)

    result = grid.clone()
    for r in range(9):
        for c in range(9):
            result.cells[r][c] = solver.value(cells[r][c])
    return SolverOutput(success=result.is_solved(), nodes_explored=counter.count)
