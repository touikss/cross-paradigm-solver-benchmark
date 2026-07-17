"""Plateau de Puissance 4 (Connect Four), 7 colonnes x 6 lignes."""

from __future__ import annotations

N_COLS = 7
N_ROWS = 6

PLAYER_1 = 1
PLAYER_2 = -1
EMPTY = 0

_CENTER_ORDER = sorted(range(N_COLS), key=lambda c: abs(c - N_COLS // 2))


class Board:
    def __init__(self, cells: list[list[int]] | None = None, to_move: int = PLAYER_1):
        # cells[col][row], row 0 = bas de la grille
        self.cells = cells if cells is not None else [[EMPTY] * N_ROWS for _ in range(N_COLS)]
        self.to_move = to_move

    def clone(self) -> "Board":
        return Board([col[:] for col in self.cells], self.to_move)

    def legal_moves(self) -> list[int]:
        return [c for c in range(N_COLS) if self.cells[c][N_ROWS - 1] == EMPTY]

    def ordered_moves(self) -> list[int]:
        """Coups legaux tries par proximite au centre (meilleurs coups en
        premier au Puissance 4). Utilise par minimax ET alpha-beta : meme
        ordre de parcours pour les deux, pour que l'elagage alpha-beta ne
        fasse QUE couper des noeuds sans jamais changer le coup choisi en cas
        d'egalite de valeur (sinon les deux peuvent diverger sur des coups
        equivalents et jouer des parties differentes)."""
        legal = set(self.legal_moves())
        return [c for c in _CENTER_ORDER if c in legal]

    def height(self, col: int) -> int:
        for r in range(N_ROWS):
            if self.cells[col][r] == EMPTY:
                return r
        return N_ROWS

    def play(self, col: int) -> "Board":
        """Retourne un nouveau plateau apres avoir joue dans col (immutable)."""
        board = self.clone()
        row = board.height(col)
        board.cells[col][row] = self.to_move
        board.to_move = -self.to_move
        return board

    def play_inplace(self, col: int) -> int:
        """Joue dans col en place, retourne la ligne jouee (pour undo)."""
        row = self.height(col)
        self.cells[col][row] = self.to_move
        self.to_move = -self.to_move
        return row

    def undo_inplace(self, col: int, row: int) -> None:
        self.cells[col][row] = EMPTY
        self.to_move = -self.to_move

    def is_full(self) -> bool:
        return all(self.cells[c][N_ROWS - 1] != EMPTY for c in range(N_COLS))

    def winner(self) -> int | None:
        """Retourne PLAYER_1/PLAYER_2 si victoire, None sinon."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for c in range(N_COLS):
            for r in range(N_ROWS):
                player = self.cells[c][r]
                if player == EMPTY:
                    continue
                for dc, dr in directions:
                    if all(
                        0 <= c + dc * i < N_COLS
                        and 0 <= r + dr * i < N_ROWS
                        and self.cells[c + dc * i][r + dr * i] == player
                        for i in range(4)
                    ):
                        return player
        return None

    def is_terminal(self) -> bool:
        return self.winner() is not None or self.is_full()

    def __str__(self) -> str:
        symbols = {PLAYER_1: "X", PLAYER_2: "O", EMPTY: "."}
        lines = []
        for r in reversed(range(N_ROWS)):
            lines.append(" ".join(symbols[self.cells[c][r]] for c in range(N_COLS)))
        return "\n".join(lines)
