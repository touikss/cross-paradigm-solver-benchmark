import pytest

from benchmark.core import NodeCounter
from benchmark.sudoku.backtracking import solve_backtracking, solve_backtracking_mrv
from benchmark.sudoku.cp_sat import solve_cp_sat
from benchmark.sudoku.dancing_links import solve_dancing_links
from benchmark.sudoku.grid import SudokuGrid
from benchmark.sudoku.instances import sample_instances
from benchmark.sudoku.smt import solve_smt

EASY_PUZZLE = (
    "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
)

EXACT_SOLVERS = [
    solve_backtracking,
    solve_backtracking_mrv,
    solve_dancing_links,
    solve_cp_sat,
    solve_smt,
]


@pytest.mark.parametrize("solver", EXACT_SOLVERS)
def test_exact_solver_solves_easy_puzzle(solver):
    grid = SudokuGrid.from_string(EASY_PUZZLE)
    counter = NodeCounter()
    output = solver(grid, counter)
    assert output.success


def test_sample_instances_are_valid_and_cover_all_difficulties():
    instances = sample_instances(n_per_difficulty=3)
    difficulties = {difficulty for _, difficulty, _ in instances}
    assert difficulties == {"easy", "medium_hard", "diabolical"}
    for _, _, grid in instances:
        assert grid.count_empty() > 0
