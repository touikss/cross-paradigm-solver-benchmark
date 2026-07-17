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


def make_solver(
    choose_move_factory: Callable[[int], ChooseMoveFn],
) -> Callable[[tuple[Board, int], NodeCounter], SolverOutput]:
    """Construit un solver (pour run_benchmark) qui joue une partie complete.

    choose_move_factory(param) renvoie la fonction de choix de coup de l'agent
    teste, parametree par le 'parametre de difficulte' de l'instance (profondeur
    de recherche pour minimax/alpha-beta, nombre de simulations pour MCTS).
    """

    def solver(instance: tuple[Board, int], counter: NodeCounter) -> SolverOutput:
        start_board, param = instance
        agent_choose_move = choose_move_factory(param)
        winner, plies = play_match(agent_choose_move, start_board, counter)
        success = winner == PLAYER_1
        return SolverOutput(
            success=success,
            nodes_explored=counter.count,
            solution_quality=float(plies),
            extra={"winner": winner},
        )

    return solver
