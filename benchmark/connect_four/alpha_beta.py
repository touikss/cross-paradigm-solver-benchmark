"""Minimax avec elagage alpha-beta. Meme heuristique et meme structure que
minimax.py, seul l'elagage change - permet de comparer directement le nombre
de noeuds explores a resultat identique."""

from __future__ import annotations

from ..core import NodeCounter
from .board import Board
from .heuristic import evaluate
from .match import make_solver

WIN_SCORE = 10_000


def _alpha_beta(
    board: Board, depth: int, alpha: float, beta: float, player: int, counter: NodeCounter
) -> float:
    counter.increment()
    winner = board.winner()
    if winner is not None:
        return WIN_SCORE if winner == player else -WIN_SCORE
    if depth == 0 or board.is_full():
        return evaluate(board, player)

    maximizing = board.to_move == player
    if maximizing:
        value = -float("inf")
        for col in board.legal_moves():
            value = max(value, _alpha_beta(board.play(col), depth - 1, alpha, beta, player, counter))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float("inf")
        for col in board.legal_moves():
            value = min(value, _alpha_beta(board.play(col), depth - 1, alpha, beta, player, counter))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def choose_move(board: Board, depth: int, counter: NodeCounter) -> int:
    player = board.to_move
    best_col = board.legal_moves()[0]
    best_value = -float("inf")
    alpha, beta = -float("inf"), float("inf")
    for col in board.legal_moves():
        value = _alpha_beta(board.play(col), depth - 1, alpha, beta, player, counter)
        if value > best_value:
            best_value = value
            best_col = col
        alpha = max(alpha, best_value)
    return best_col


solve_alpha_beta = make_solver(lambda depth: (lambda board, counter: choose_move(board, depth, counter)))
