"""Algorithm X de Knuth via Dancing Links (exact cover) applique au Sudoku.

Un 'noeud explore' correspond a un choix de ligne (case, valeur) dans la
recherche d'exact cover.
"""

from __future__ import annotations

from ..core import NodeCounter, SolverOutput
from .grid import SudokuGrid


class DLXNode:
    __slots__ = ("left", "right", "up", "down", "column", "row_info")

    def __init__(self) -> None:
        self.left = self.right = self.up = self.down = self
        self.column: "DLXColumn | None" = None
        self.row_info: tuple[int, int, int] | None = None


class DLXColumn(DLXNode):
    __slots__ = ("size", "name")

    def __init__(self, name: str) -> None:
        super().__init__()
        self.size = 0
        self.name = name
        self.column = self


def _build_exact_cover(grid: SudokuGrid) -> DLXColumn:
    n_constraints = 4 * 81
    header = DLXColumn("header")
    columns: list[DLXColumn] = []
    for i in range(n_constraints):
        col = DLXColumn(str(i))
        col.right = header
        col.left = header.left
        header.left.right = col
        header.left = col
        columns.append(col)

    def cell_constraint(r: int, c: int) -> int:
        return r * 9 + c

    def row_constraint(r: int, n: int) -> int:
        return 81 + r * 9 + (n - 1)

    def col_constraint(c: int, n: int) -> int:
        return 162 + c * 9 + (n - 1)

    def box_constraint(r: int, c: int, n: int) -> int:
        box = (r // 3) * 3 + (c // 3)
        return 243 + box * 9 + (n - 1)

    for r in range(9):
        for c in range(9):
            fixed = grid.cells[r][c]
            candidates = [fixed] if fixed != 0 else range(1, 10)
            for n in candidates:
                constraint_indices = [
                    cell_constraint(r, c),
                    row_constraint(r, n),
                    col_constraint(c, n),
                    box_constraint(r, c, n),
                ]
                first_node: DLXNode | None = None
                for idx in constraint_indices:
                    col = columns[idx]
                    node = DLXNode()
                    node.column = col
                    node.up = col.up
                    node.down = col
                    col.up.down = node
                    col.up = node
                    col.size += 1
                    node.row_info = (r, c, n)
                    if first_node is None:
                        first_node = node
                        node.left = node.right = node
                    else:
                        node.left = first_node.left
                        node.right = first_node
                        first_node.left.right = node
                        first_node.left = node
    return header


def _cover(col: DLXColumn) -> None:
    col.right.left = col.left
    col.left.right = col.right
    node = col.down
    while node is not col:
        sibling = node.right
        while sibling is not node:
            sibling.down.up = sibling.up
            sibling.up.down = sibling.down
            sibling.column.size -= 1
            sibling = sibling.right
        node = node.down


def _uncover(col: DLXColumn) -> None:
    node = col.up
    while node is not col:
        sibling = node.left
        while sibling is not node:
            sibling.column.size += 1
            sibling.down.up = sibling
            sibling.up.down = sibling
            sibling = sibling.left
        node = node.up
    col.right.left = col
    col.left.right = col


def _search(header: DLXColumn, solution: list[DLXNode], counter: NodeCounter) -> bool:
    if header.right is header:
        return True

    col = header.right
    best = col
    while col is not header:
        if col.size < best.size:
            best = col
        col = col.right
    col = best

    if col.size == 0:
        return False

    _cover(col)
    row = col.down
    while row is not col:
        counter.increment()
        solution.append(row)
        node = row.right
        while node is not row:
            _cover(node.column)
            node = node.right

        if _search(header, solution, counter):
            return True

        solution.pop()
        node = row.left
        while node is not row:
            _uncover(node.column)
            node = node.left
        row = row.down

    _uncover(col)
    return False


def solve_dancing_links(grid: SudokuGrid, counter: NodeCounter) -> SolverOutput:
    header = _build_exact_cover(grid)
    solution: list[DLXNode] = []
    success = _search(header, solution, counter)
    if not success:
        return SolverOutput(success=False, nodes_explored=counter.count)

    result = grid.clone()
    for node in solution:
        r, c, n = node.row_info
        result.cells[r][c] = n
    return SolverOutput(success=result.is_solved(), nodes_explored=counter.count)
