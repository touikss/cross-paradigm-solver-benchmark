"""Common data model and orchestration of the cross-paradigm benchmark."""

from __future__ import annotations

import os
import resource
import signal
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterable

import pandas as pd


@dataclass
class SolverOutput:
    """Raw result returned by a solver, before time/memory measurement."""

    success: bool
    nodes_explored: int
    solution_quality: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Metrics:
    """One benchmark result row, uniform across games/paradigms."""

    game: str
    paradigm: str
    instance_id: str
    difficulty: str | int
    success: bool
    time_seconds: float
    peak_memory_mb: float
    nodes_explored: int
    solution_quality: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        extra = row.pop("extra")
        row.update({f"extra_{k}": v for k, v in extra.items()})
        return row


Solver = Callable[[Any, "NodeCounter"], SolverOutput]


class NodeCounter:
    """Counter of 'explored nodes' incremented by a solver during its search.

    What a node means varies by paradigm family (see README/notebook): decision
    or assignment tested (backtracking, DLX, CP-SAT, SMT), game-tree node
    visited (minimax, alpha-beta, MCTS), fitness evaluation (GA, simulated
    annealing), or candidate word evaluated (Wordle). This counter only
    increments; the semantics are documented at each solver.
    """

    def __init__(self) -> None:
        self.count = 0

    def increment(self, n: int = 1) -> None:
        self.count += n


class InstanceTimeout(Exception):
    pass


@contextmanager
def _time_limit(seconds: float):
    """Interrupt the block via SIGALRM if `seconds` is exceeded. Works in the
    main thread of any process (including a separate worker launched by
    ProcessPoolExecutor, which has its own main thread). Does not interrupt a
    blocking C call that never returns control to the interpreter (not
    relevant here: the slow solvers are pure Python)."""

    def _handler(signum, frame):
        raise InstanceTimeout()

    old_handler = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


def _measure_instance(
    solver: Solver, instance_data: Any, timeout_seconds: float
) -> tuple[SolverOutput, float, float]:
    """Run a solver on an instance with time/memory measurement and a time
    budget. Top-level function (picklable) so it can run in a
    ProcessPoolExecutor worker.

    Memory is measured via ru_maxrss (process peak memory, in KB) rather than
    tracemalloc: tracemalloc traces every individual allocation and slows
    down allocation-heavy solvers (GA, simulated annealing) by a factor of
    4-10x, which skewed the timing measurements. ru_maxrss is nearly free and,
    since each worker handles only one instance, it closely approximates the
    peak memory of that solve.
    """
    counter = NodeCounter()
    try:
        with _time_limit(timeout_seconds):
            start = time.perf_counter()
            output = solver(instance_data, counter)
            elapsed = time.perf_counter() - start
            peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            return output, elapsed, peak_mb
    except InstanceTimeout:
        output = SolverOutput(
            success=False, nodes_explored=counter.count, extra={"timed_out": True}
        )
        return output, timeout_seconds, float("nan")


def _to_metrics(
    game: str,
    paradigm: str,
    instance_id: str,
    difficulty: str | int,
    output: SolverOutput,
    elapsed: float,
    peak_mem: float,
) -> Metrics:
    return Metrics(
        game=game,
        paradigm=paradigm,
        instance_id=instance_id,
        difficulty=difficulty,
        success=output.success,
        time_seconds=elapsed,
        peak_memory_mb=peak_mem,
        nodes_explored=output.nodes_explored,
        solution_quality=output.solution_quality,
        extra=output.extra,
    )


def run_benchmark(
    game: str,
    paradigm: str,
    solver: Solver,
    instances: Iterable[tuple[str, str | int, Any]],
    timeout_seconds: float = 120.0,
) -> list[Metrics]:
    """Run a solver sequentially on a list of instances.

    instances: iterable of (instance_id, difficulty, instance_data)
    timeout_seconds: if an instance exceeds this budget, it is counted as a
        failure (timeout) and we move on to the next one rather than blocking
        the whole benchmark.
    """
    results: list[Metrics] = []
    for instance_id, difficulty, instance_data in instances:
        output, elapsed, peak_mem = _measure_instance(solver, instance_data, timeout_seconds)
        if output.extra.get("timed_out"):
            print(f"    [timeout] {game}/{paradigm}/{instance_id} > {timeout_seconds}s, skip")
        results.append(
            _to_metrics(game, paradigm, instance_id, difficulty, output, elapsed, peak_mem)
        )
    return results


def run_benchmark_parallel(
    game: str,
    paradigm: str,
    solver: Solver,
    instances: Iterable[tuple[str, str | int, Any]],
    timeout_seconds: float = 120.0,
    max_workers: int | None = None,
) -> list[Metrics]:
    """Like run_benchmark, but distributes instances across several processes
    (instances of a given solver are independent). The time budget is applied
    in each worker via SIGALRM: an instance that exceeds the budget
    interrupts itself and frees its worker for the next task.

    `solver` must be a top-level (picklable) function - no lambda or closure
    returned by a factory.
    """
    max_workers = max_workers or max(1, (os.cpu_count() or 2) - 1)
    instances = list(instances)
    results: list[Metrics] = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_meta = {
            executor.submit(_measure_instance, solver, instance_data, timeout_seconds): (
                instance_id,
                difficulty,
            )
            for instance_id, difficulty, instance_data in instances
        }
        for future in as_completed(future_to_meta):
            instance_id, difficulty = future_to_meta[future]
            output, elapsed, peak_mem = future.result()
            if output.extra.get("timed_out"):
                print(f"    [timeout] {game}/{paradigm}/{instance_id} > {timeout_seconds}s, skip")
            results.append(
                _to_metrics(game, paradigm, instance_id, difficulty, output, elapsed, peak_mem)
            )
    return results


def metrics_to_dataframe(metrics: Iterable[Metrics]) -> pd.DataFrame:
    return pd.DataFrame([m.to_row() for m in metrics])
