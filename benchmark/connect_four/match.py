"""Fait jouer un agent teste contre un adversaire de reference fixe
(alpha-beta profondeur 4) sur une partie complete, plutot qu'un tournoi
tous-contre-tous - plus interpretable pour comparer des paradigmes
heterogenes (voir notebook)."""

from __future__ import annotations

from typing import Callable

from ..core import NodeCounter, SolverOutput
from .board import Board, PLAYER_1

ChooseMoveFn = Callable[[Board, NodeCounter], int]

REFERENCE_DEPTH = 4


def _reference_choose_move(board: Board, _counter: NodeCounter) -> int:
    from . import alpha_beta  # import tardif : evite un cycle avec alpha_beta.py

    return alpha_beta.choose_move(board, REFERENCE_DEPTH, NodeCounter())


def play_match(
    agent_choose_move: ChooseMoveFn,
    start_board: Board,
    counter: NodeCounter,
    agent_plays: int = PLAYER_1,
) -> tuple[int | None, int]:
    """Joue une partie complete. Retourne (gagnant ou None si nulle, nb de coups)."""
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
    """Joue une partie complete et empaquette le resultat en SolverOutput.

    Utilise par les solve_* de chaque module (minimax.py, alpha_beta.py, ...),
    qui doivent rester des fonctions top-level (picklables pour le
    multiprocessing) plutot que des closures produites par une factory.
    """
    winner, plies = play_match(agent_choose_move, start_board, counter)
    success = winner == PLAYER_1
    return SolverOutput(
        success=success,
        nodes_explored=counter.count,
        solution_quality=float(plies),
        extra={"winner": winner},
    )
