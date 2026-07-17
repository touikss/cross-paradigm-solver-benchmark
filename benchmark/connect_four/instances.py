"""Instances de benchmark Connect Four : position de depart (plateau vide) +
parametre de 'difficulte' de recherche.

Pour minimax/alpha-beta/baseline, la difficulte = profondeur de recherche
(1 a 10). Pour MCTS, qui n'a pas de profondeur fixe, la difficulte est
convertie en un nombre de simulations equivalent (voir notebook pour la
discussion budget-temps vs profondeur-fixe).
"""

from __future__ import annotations

from .board import Board

DEPTHS = list(range(1, 11))
MCTS_SIMULATIONS_PER_DEPTH = 50  # facteur d'echelle simulations ~ profondeur


def depth_instances(n_per_depth: int = 1) -> list[tuple[str, int, tuple[Board, int]]]:
    instances = []
    for depth in DEPTHS:
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
