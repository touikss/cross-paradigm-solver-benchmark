"""Greedy agent (naive baseline): plays the move that maximizes the heuristic at
a single ply (no opponent lookahead). Serves as a low-end reference against
minimax/alpha-beta/MCTS. An 'explored node' = one candidate move evaluated."""

from __future__ import annotations

from ..core import NodeCounter, SolverOutput
from .board import Board
from .heuristic import evaluate
from .match import run_match_solver


def choose_move(board: Board, counter: NodeCounter) -> int:
    player = board.to_move
    best_col = board.legal_moves()[0]
    best_value = -float("inf")
    for col in board.legal_moves():
        counter.increment()
        value = evaluate(board.play(col), player)
        if value > best_value:
            best_value = value
            best_col = col
    return best_col


def solve_baseline(instance: tuple[Board, int], counter: NodeCounter) -> SolverOutput:
    board, _param = instance
    return run_match_solver(choose_move, board, counter)
