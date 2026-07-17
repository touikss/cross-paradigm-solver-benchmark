"""Lance tous les benchmarks (Sudoku, Connect Four, Wordle) et sauvegarde les
resultats en CSV dans results/. A executer une fois via
`uv run python -m benchmark.run_all` ; le notebook se contente ensuite de
recharger les CSV (evite de relancer GA/MCTS a chaque execution du notebook).
"""

from __future__ import annotations

import time
from pathlib import Path

from .core import Metrics, metrics_to_dataframe, run_benchmark
from .instrumentation import measure

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def run_sudoku() -> list[Metrics]:
    from .sudoku.backtracking import solve_backtracking, solve_backtracking_mrv
    from .sudoku.cp_sat import solve_cp_sat
    from .sudoku.dancing_links import solve_dancing_links
    from .sudoku.genetic import solve_genetic
    from .sudoku.instances import sample_instances
    from .sudoku.simulated_annealing import solve_simulated_annealing
    from .sudoku.smt import solve_smt

    instances = sample_instances(n_per_difficulty=10)
    solvers = {
        "backtracking": solve_backtracking,
        "backtracking_mrv": solve_backtracking_mrv,
        "dancing_links": solve_dancing_links,
        "genetic": solve_genetic,
        "simulated_annealing": solve_simulated_annealing,
        "cp_sat": solve_cp_sat,
        "smt": solve_smt,
    }
    results: list[Metrics] = []
    for name, solver in solvers.items():
        print(f"  sudoku/{name}...")
        t0 = time.perf_counter()
        results.extend(run_benchmark("sudoku", name, solver, instances, measure))
        print(f"    done in {time.perf_counter() - t0:.1f}s")
    return results


def run_connect_four() -> list[Metrics]:
    from .connect_four.alpha_beta import solve_alpha_beta
    from .connect_four.baseline import solve_baseline
    from .connect_four.instances import (
        ALPHA_BETA_DEPTHS,
        MINIMAX_DEPTHS,
        depth_instances,
        mcts_instances,
    )
    from .connect_four.minimax import solve_minimax
    from .connect_four.mcts import solve_mcts

    results: list[Metrics] = []
    depth_solvers = {
        "minimax": (solve_minimax, MINIMAX_DEPTHS),
        "alpha_beta": (solve_alpha_beta, ALPHA_BETA_DEPTHS),
        "baseline": (solve_baseline, None),
    }
    for name, (solver, depths) in depth_solvers.items():
        print(f"  connect_four/{name}...")
        t0 = time.perf_counter()
        instances = depth_instances(n_per_depth=1, depths=depths)
        results.extend(run_benchmark("connect_four", name, solver, instances, measure))
        print(f"    done in {time.perf_counter() - t0:.1f}s")

    print("  connect_four/mcts...")
    t0 = time.perf_counter()
    results.extend(
        run_benchmark("connect_four", "mcts", solve_mcts, mcts_instances(n_per_depth=1), measure)
    )
    print(f"    done in {time.perf_counter() - t0:.1f}s")
    return results


def run_wordle() -> list[Metrics]:
    from .wordle.bayesian_elimination import solve_bayesian_elimination
    from .wordle.csp_solver import solve_csp
    from .wordle.entropy_solver import solve_entropy
    from .wordle.instances import sample_instances

    instances = sample_instances(n_per_length=10)
    solvers = {
        "bayesian_elimination": solve_bayesian_elimination,
        "entropy": solve_entropy,
        "csp": solve_csp,
    }
    results: list[Metrics] = []
    for name, solver in solvers.items():
        print(f"  wordle/{name}...")
        t0 = time.perf_counter()
        results.extend(run_benchmark("wordle", name, solver, instances, measure))
        print(f"    done in {time.perf_counter() - t0:.1f}s")
    return results


def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)

    print("Sudoku...")
    sudoku_df = metrics_to_dataframe(run_sudoku())
    sudoku_df.to_csv(RESULTS_DIR / "sudoku_results.csv", index=False)

    print("Connect Four...")
    connect_four_df = metrics_to_dataframe(run_connect_four())
    connect_four_df.to_csv(RESULTS_DIR / "connect_four_results.csv", index=False)

    print("Wordle...")
    wordle_df = metrics_to_dataframe(run_wordle())
    wordle_df.to_csv(RESULTS_DIR / "wordle_results.csv", index=False)

    print("Termine. Resultats dans results/*.csv")


if __name__ == "__main__":
    main()
