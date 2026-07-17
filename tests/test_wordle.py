import pytest

from benchmark.core import NodeCounter
from benchmark.wordle.bayesian_elimination import solve_bayesian_elimination
from benchmark.wordle.csp_solver import solve_csp
from benchmark.wordle.entropy_solver import solve_entropy
from benchmark.wordle.game import get_feedback, is_win
from benchmark.wordle.instances import sample_instances


def test_feedback_all_green_on_exact_match():
    assert get_feedback("crane", "crane") == "GGGGG"
    assert is_win("GGGGG")


def test_feedback_handles_duplicate_letters():
    # target 'allow' a deux 'l' ; guess 'lulls' a deux 'l' aussi
    feedback = get_feedback("lulls", "allow")
    assert feedback[0] in ("Y", "G")
    assert not is_win(feedback)


def test_feedback_marks_absent_letter_as_gray():
    assert get_feedback("zzzzz", "crane") == "XXXXX"


@pytest.mark.parametrize(
    "solver", [solve_bayesian_elimination, solve_csp, solve_entropy]
)
def test_solvers_converge_on_a_sample_of_5_letter_words(solver):
    instances = [i for i in sample_instances(n_per_length=3) if i[1] == 5]
    for _instance_id, _length, data in instances:
        counter = NodeCounter()
        output = solver(data, counter)
        assert output.success
        assert output.solution_quality is not None and 1 <= output.solution_quality <= 6
