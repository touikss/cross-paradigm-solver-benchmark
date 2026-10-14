"""Plays a tested agent against a fixed reference opponent (alpha-beta depth 4)
over one full game, rather than an all-vs-all tournament; more interpretable
for comparing heterogeneous paradigms (see notebook)."""

from __future__ import annotations

from typing import Callable

from ..core import NodeCounter, SolverOutput
from .board import PLAYER_1, Board

ChooseMoveFn = Callable[[Board, NodeCounter], int]

REFERENCE_DEPTH = 4


def _reference_choose_move(board: Board, _counter: NodeCounter) -> int:
    from . import alpha_beta  # late import: avoids a cycle with alpha_beta.py

    return alpha_beta.choose_move(board, REFERENCE_DEPTH, NodeCounter())


def play_match(
    agent_choose_move: ChooseMoveFn,
    start_board: Board,
    counter: NodeCounter,
    agent_plays: int = PLAYER_1,
) -> tuple[int | None, int]:
    """Play one full game. Return (winner or None if draw, number of moves)."""
    board = start_board.clone()
    plies = 0
    while not board.is_terminal():
        if board.to_move == agent_plays:
            move = agent_choose_move(board, counter)
        else:
            move = _reference_choose_move(board, counter)
        board = board.play(move)
        plies += 1
    return board.winner(), plies


def run_match_solver(
    agent_choose_move: ChooseMoveFn, start_board: Board, counter: NodeCounter
) -> SolverOutput:
    """Play one full game and package the result as a SolverOutput.

    Used by each module's solve_* functions (minimax.py, alpha_beta.py, ...),
    which must remain top-level functions (picklable for multiprocessing)
    rather than closures produced by a factory.
    """
    winner, plies = play_match(agent_choose_move, start_board, counter)
    success = winner == PLAYER_1
    return SolverOutput(
        success=success,
        nodes_explored=counter.count,
        solution_quality=float(plies),
        extra={"winner": winner},
    )
