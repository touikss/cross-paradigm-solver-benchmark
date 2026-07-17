"""Satisfiabilite modulo theories (SMT) via Z3.

Un 'noeud explore' correspond au nombre de decisions prises par le solveur
Z3, recupere via ses statistiques internes ('decisions').
"""

from __future__ import annotations

import z3

from ..core import NodeCounter, SolverOutput
from .grid import SudokuGrid


def solve_smt(grid: SudokuGrid, counter: NodeCounter) -> SolverOutput:
    solver = z3.Solver()
    cells = [[z3.Int(f"c_{r}_{c}") for c in range(9)] for r in range(9)]

    for row in cells:
        for cell in row:
            solver.add(cell >= 1, cell <= 9)

    for r in range(9):
        solver.add(z3.Distinct(cells[r]))
    for c in range(9):
        solver.add(z3.Distinct([cells[r][c] for r in range(9)]))
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            solver.add(
                z3.Distinct(
                    [
                        cells[r][c]
                        for r in range(box_row, box_row + 3)
                        for c in range(box_col, box_col + 3)
                    ]
                )
            )
    for r in range(9):
        for c in range(9):
            if grid.cells[r][c] != 0:
                solver.add(cells[r][c] == grid.cells[r][c])

    status = solver.check()
    stats = solver.statistics()
    decisions = 0
    for key, value in stats:
        if key == "decisions":
            decisions = int(value)
            break
    counter.increment(decisions)

    if status != z3.sat:
        return SolverOutput(success=False, nodes_explored=counter.count)

    model = solver.model()
    result = grid.clone()
    for r in range(9):
        for c in range(9):
            result.cells[r][c] = model.evaluate(cells[r][c]).as_long()
    return SolverOutput(success=result.is_solved(), nodes_explored=counter.count)
