import pytest

from benchmark.connect_four.board import Board, PLAYER_1, PLAYER_2
from benchmark.connect_four.alpha_beta import solve_alpha_beta
from benchmark.connect_four.baseline import solve_baseline
from benchmark.connect_four.minimax import solve_minimax
from benchmark.connect_four.mcts import solve_mcts
from benchmark.core import NodeCounter


def test_legal_moves_on_empty_board():
    board = Board()
    assert board.legal_moves() == list(range(7))


def test_horizontal_win_detected():
    board = Board()
    for col in [0, 0, 1, 1, 2, 2, 3]:
        board = board.play(col)
    assert board.winner() == PLAYER_1


def test_column_fills_up_and_is_no_longer_legal():
    board = Board()
    for _ in range(6):
        board = board.play(0)
    assert 0 not in board.legal_moves()


def test_full_board_is_terminal():
    board = Board()
    assert not board.is_terminal()


@pytest.mark.parametrize(
    "solver,param",
    [(solve_minimax, 3), (solve_alpha_beta, 3), (solve_baseline, 0), (solve_mcts, 50)],
)
def test_solvers_play_a_full_valid_game(solver, param):
    counter = NodeCounter()
    output = solver((Board(), param), counter)
    assert output.nodes_explored > 0
    assert output.solution_quality is not None and output.solution_quality > 0
