"""Fonction d'evaluation heuristique partagee par minimax/alpha-beta/expectimax.

Compte les alignements ouverts de 2 et 3 pions (fenetres de 4 cases contenant
uniquement les pions d'un joueur + des cases vides), pondere par la proximite
du centre (plus de fenetres possibles au centre).
"""

from __future__ import annotations

from .board import Board, EMPTY, N_COLS, N_ROWS

CENTER_COL = N_COLS // 2
WINDOW_SCORES = {2: 2, 3: 5, 4: 1000}


def _windows(board: Board):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for c in range(N_COLS):
        for r in range(N_ROWS):
            for dc, dr in directions:
                cells = [
                    (c + dc * i, r + dr * i)
                    for i in range(4)
                    if 0 <= c + dc * i < N_COLS and 0 <= r + dr * i < N_ROWS
                ]
                if len(cells) == 4:
                    yield [board.cells[cc][rr] for cc, rr in cells]


def evaluate(board: Board, player: int) -> float:
    score = 0.0
    for window in _windows(board):
        player_count = window.count(player)
        opponent_count = window.count(-player)
        if player_count > 0 and opponent_count > 0:
            continue
        if player_count > 0:
            score += WINDOW_SCORES.get(player_count, 0)
        elif opponent_count > 0:
            score -= WINDOW_SCORES.get(opponent_count, 0)

    for c in range(N_COLS):
        weight = 3 - abs(c - CENTER_COL)
        for r in range(N_ROWS):
            if board.cells[c][r] == player:
                score += weight * 0.1
            elif board.cells[c][r] == -player:
                score -= weight * 0.1
    return score
