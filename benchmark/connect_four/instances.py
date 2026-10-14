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
# Minimax has no pruning: at depth >= 7 a full game becomes impractical in
# reasonable time (combinatorial explosion, precisely what the benchmark is
# meant to illustrate against alpha-beta).
MINIMAX_DEPTHS = list(range(1, 7))
# Even with pruning + center-first move ordering, depth 10 pushes a full game
# to several minutes (~x7 per extra depth level); the exponential trend is
# already very clear at 9.
ALPHA_BETA_DEPTHS = list(range(1, 10))
MCTS_SIMULATIONS_PER_DEPTH = 50  # scale factor: simulations ~ depth


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
