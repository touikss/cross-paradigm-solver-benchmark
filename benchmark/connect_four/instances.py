"""Connect Four benchmark instances: starting position (empty board) + search
'difficulty' parameter.

For minimax/alpha-beta/baseline, difficulty = search depth (1 to 10). For
MCTS, which has no fixed depth, difficulty is converted into an equivalent
number of simulations (see the notebook for the time-budget vs fixed-depth
discussion).
"""

from __future__ import annotations

from .board import Board

DEPTHS = list(range(1, 11))
MINIMAX_DEPTHS = list(range(1, 7))
ALPHA_BETA_DEPTHS = list(range(1, 10))
MCTS_SIMULATIONS_PER_DEPTH = 50


def depth_instances(
    n_per_depth: int = 1, depths: list[int] | None = None
) -> list[tuple[str, int, tuple[Board, int]]]:
    instances = []
    for depth in depths if depths is not None else DEPTHS:
        for i in range(n_per_depth):
            instance_id = f"depth{depth}_{i}"
            instances.append((instance_id, depth, (Board(), depth)))
    return instances


def mcts_instances(n_per_depth: int = 1) -> list[tuple[str, int, tuple[Board, int]]]:
    instances = []
    for depth in DEPTHS:
        n_simulations = depth * MCTS_SIMULATIONS_PER_DEPTH
        for i in range(n_per_depth):
            instance_id = f"depth{depth}_{i}"
            instances.append((instance_id, depth, (Board(), n_simulations)))
    return instances
