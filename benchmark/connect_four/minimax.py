"""Minimax a profondeur bornee (sans elagage). Un 'noeud explore' = un appel
recursif de _minimax (un noeud de l'arbre de jeu visite)."""

from __future__ import annotations

from ..core import NodeCounter
from .board import Board
from .heuristic import evaluate
from .match import make_solver

WIN_SCORE = 10_000


def _minimax(board: Board, depth: int, player: int, counter: NodeCounter) -> float:
    counter.increment()
    winner = board.winner()
    if winner is not None:
        return WIN_SCORE if winner == player else -WIN_SCORE
    if depth == 0 or board.is_full():
        return evaluate(board, player)

    moves = board.legal_moves()
    maximizing = board.to_move == player
    best = -float("inf") if maximizing else float("inf")
    for col in moves:
        value = _minimax(board.play(col), depth - 1, player, counter)
        if maximizing:
            best = max(best, value)
        else:
            best = min(best, value)
    return best


def choose_move(board: Board, depth: int, counter: NodeCounter) -> int:
    player = board.to_move
    best_col = board.legal_moves()[0]
    best_value = -float("inf")
    for col in board.legal_moves():
        value = _minimax(board.play(col), depth - 1, player, counter)
        if value > best_value:
            best_value = value
            best_col = col
    return best_col


solve_minimax = make_solver(lambda depth: (lambda board, counter: choose_move(board, depth, counter)))
