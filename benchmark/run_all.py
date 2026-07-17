"""Lance tous les benchmarks (Sudoku, Connect Four, Wordle) et sauvegarde les
resultats en CSV dans results/. A executer une fois via
`uv run python -m benchmark.run_all` ; le notebook se contente ensuite de
recharger les CSV (evite de relancer GA/MCTS a chaque execution du notebook).

Chaque instance est executee dans un processus separe (ProcessPoolExecutor) :
les instances d'un meme solveur sont independantes, donc parallelisables sans
effort particulier. Le CSV d'un jeu est reecrit apres CHAQUE solveur (pas
seulement en fin de jeu), pour ne rien perdre si le script est interrompu.
"""

from __future__ import annotations

import time
from pathlib import Path

from .core import Metrics, metrics_to_dataframe, run_benchmark_parallel

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def _run_and_checkpoint(
    game: str,
    solvers: dict[str, tuple],
    csv_path: Path,
    default_instances=None,
) -> list[Metrics]:
    """Lance chaque solveur de `solvers` (nom -> (solver, instances_ou_None))
    et reecrit le CSV apres chaque solveur termine."""
    results: list[Metrics] = []
    for name, (solver, instances) in solvers.items():
        instances = instances if instances is not None else default_instances
        print(f"  {game}/{name}...")
        t0 = time.perf_counter()
        results.extend(run_benchmark_parallel(game, name, solver, instances))
        print(f"    done in {time.perf_counter() - t0:.1f}s")
        metrics_to_dataframe(results).to_csv(csv_path, index=False)
    return results


def run_sudoku(csv_path: Path) -> list[Metrics]:
    from .sudoku.backtracking import solve_backtracking, solve_backtracking_mrv
    from .sudoku.cp_sat import solve_cp_sat
    from .sudoku.dancing_links import solve_dancing_links
    from .sudoku.genetic import solve_genetic
    from .sudoku.instances import sample_instances
    from .sudoku.simulated_annealing import solve_simulated_annealing
    from .sudoku.smt import solve_smt

    instances = sample_instances(n_per_difficulty=10)
    solvers = {
        "backtracking": (solve_backtracking, None),
        "backtracking_mrv": (solve_backtracking_mrv, None),
        "dancing_links": (solve_dancing_links, None),
        "genetic": (solve_genetic, None),
        "simulated_annealing": (solve_simulated_annealing, None),
        "cp_sat": (solve_cp_sat, None),
        "smt": (solve_smt, None),
    }
    return _run_and_checkpoint("sudoku", solvers, csv_path, default_instances=instances)


def run_connect_four(csv_path: Path) -> list[Metrics]:
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

    solvers = {
        "minimax": (solve_minimax, depth_instances(n_per_depth=1, depths=MINIMAX_DEPTHS)),
        "alpha_beta": (solve_alpha_beta, depth_instances(n_per_depth=1, depths=ALPHA_BETA_DEPTHS)),
        "baseline": (solve_baseline, depth_instances(n_per_depth=1)),
        "mcts": (solve_mcts, mcts_instances(n_per_depth=1)),
    }
    return _run_and_checkpoint("connect_four", solvers, csv_path)


def run_wordle(csv_path: Path) -> list[Metrics]:
    from .wordle.bayesian_elimination import solve_bayesian_elimination
    from .wordle.csp_solver import solve_csp
    from .wordle.entropy_solver import solve_entropy
    from .wordle.instances import sample_instances

    instances = sample_instances(n_per_length=10)
    solvers = {
        "bayesian_elimination": (solve_bayesian_elimination, None),
        "entropy": (solve_entropy, None),
        "csp": (solve_csp, None),
    }
    return _run_and_checkpoint("wordle", solvers, csv_path, default_instances=instances)


def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)

    print("Sudoku...")
    run_sudoku(RESULTS_DIR / "sudoku_results.csv")

    print("Connect Four...")
    run_connect_four(RESULTS_DIR / "connect_four_results.csv")

    print("Wordle...")
    run_wordle(RESULTS_DIR / "wordle_results.csv")

    print("Termine. Resultats dans results/*.csv")


if __name__ == "__main__":
    main()
