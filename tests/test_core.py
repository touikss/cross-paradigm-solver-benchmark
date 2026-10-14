"""Tests of the measurement framework (benchmark/core.py)."""

import time

from benchmark.core import (
    Metrics,
    NodeCounter,
    SolverOutput,
    _measure_instance,
    metrics_to_dataframe,
    run_benchmark,
    run_benchmark_parallel,
)
from benchmark.sudoku.dancing_links import solve_dancing_links
from benchmark.sudoku.instances import sample_instances


def _instant_solver(instance, counter: NodeCounter) -> SolverOutput:
    counter.increment(3)
    return SolverOutput(success=True, nodes_explored=counter.count, solution_quality=1.5)


def _sleeping_solver(instance, counter: NodeCounter) -> SolverOutput:
    counter.increment(1)
    time.sleep(5)
    return SolverOutput(success=True, nodes_explored=counter.count)


def test_measure_instance_returns_output_and_timing():
    output, elapsed, peak_mb = _measure_instance(_instant_solver, None, timeout_seconds=5)
    assert output.success and output.nodes_explored == 3
    assert 0 <= elapsed < 5
    assert peak_mb > 0


def test_timeout_is_recorded_as_a_failure():
    start = time.perf_counter()
    output, elapsed, _ = _measure_instance(_sleeping_solver, None, timeout_seconds=0.2)
    assert time.perf_counter() - start < 2
    assert output.success is False
    assert output.extra == {"timed_out": True}
    assert output.nodes_explored == 1
    assert elapsed == 0.2


def test_metrics_row_flattens_extra_fields():
    metrics = Metrics(
        game="g",
        paradigm="p",
        instance_id="i",
        difficulty="easy",
        success=True,
        time_seconds=0.1,
        peak_memory_mb=50.0,
        nodes_explored=7,
        extra={"winner": 1},
    )
    row = metrics.to_row()
    assert row["extra_winner"] == 1
    assert "extra" not in row
    assert list(metrics_to_dataframe([metrics]).columns)[-1] == "extra_winner"


def test_sequential_runner_keeps_input_order():
    instances = [("a", "easy", None), ("b", "easy", None), ("c", "hard", None)]
    results = run_benchmark("g", "p", _instant_solver, instances)
    assert [m.instance_id for m in results] == ["a", "b", "c"]
    assert all(m.success and m.solution_quality == 1.5 for m in results)


def test_parallel_runner_returns_rows_in_input_order():
    instances = sample_instances(n_per_difficulty=2)
    results = run_benchmark_parallel(
        "sudoku", "dancing_links", solve_dancing_links, instances, max_workers=2
    )
    assert [m.instance_id for m in results] == [instance[0] for instance in instances]
    assert all(m.success for m in results)
