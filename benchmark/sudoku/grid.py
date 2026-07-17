from __future__ import annotations

from typing import List, Optional, Tuple


class SudokuGrid:
    """Representation d'une grille de Sudoku 9x9."""

    def __init__(self, grid: Optional[List[List[int]]] = None):
        if grid is None:
            self.cells = [[0] * 9 for _ in range(9)]
        else:
            self.cells = [row[:] for row in grid]

    @classmethod
    def from_string(cls, s: str) -> "SudokuGrid":
        s = s.replace(".", "0").replace(" ", "").replace("\n", "")
        if len(s) != 81:
            raise ValueError(f"La chaine doit avoir 81 caracteres, recu {len(s)}")

        grid = cls()
        for i in range(81):
            grid.cells[i // 9][i % 9] = int(s[i])
        return grid

    def clone(self) -> "SudokuGrid":
        return SudokuGrid(self.cells)

    def is_valid_placement(self, row: int, col: int, num: int) -> bool:
        if num in self.cells[row]:
            return False
        if num in [self.cells[r][col] for r in range(9)]:
            return False
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.cells[r][c] == num:
                    return False
        return True

    def find_empty(self) -> Optional[Tuple[int, int]]:
        for r in range(9):
            for c in range(9):
                if self.cells[r][c] == 0:
                    return (r, c)
        return None

    def find_empty_mrv(self) -> Optional[Tuple[int, int]]:
        """Cellule vide avec le moins de candidats possibles (Minimum Remaining Values)."""
        best: Optional[Tuple[int, int]] = None
        best_count = 10
        for r in range(9):
            for c in range(9):
                if self.cells[r][c] != 0:
                    continue
                count = sum(1 for n in range(1, 10) if self.is_valid_placement(r, c, n))
                if count < best_count:
                    best, best_count = (r, c), count
                    if count == 0:
                        return best
        return best

    def is_complete(self) -> bool:
        return all(self.cells[r][c] != 0 for r in range(9) for c in range(9))

    def is_solved(self) -> bool:
        """Grille complete ET valide (lignes/colonnes/blocs sans doublon)."""
        if not self.is_complete():
            return False
        digits = set(range(1, 10))
        for r in range(9):
            if set(self.cells[r]) != digits:
                return False
        for c in range(9):
            if {self.cells[r][c] for r in range(9)} != digits:
                return False
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box = {
                    self.cells[r][c]
                    for r in range(box_row, box_row + 3)
                    for c in range(box_col, box_col + 3)
                }
                if box != digits:
                    return False
        return True

    def count_empty(self) -> int:
        return sum(1 for r in range(9) for c in range(9) if self.cells[r][c] == 0)

    def to_string(self) -> str:
        return "".join(str(self.cells[r][c]) for r in range(9) for c in range(9))

    def __str__(self) -> str:
        lines = []
        for r in range(9):
            if r > 0 and r % 3 == 0:
                lines.append("-" * 21)
            row_str = ""
            for c in range(9):
                if c > 0 and c % 3 == 0:
                    row_str += "| "
                val = self.cells[r][c]
                row_str += (str(val) if val != 0 else ".") + " "
            lines.append(row_str)
        return "\n".join(lines)
