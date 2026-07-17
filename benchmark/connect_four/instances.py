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
# Minimax n'a pas d'elagage : a profondeur >= 7 une partie complete devient
# impraticable en temps raisonnable (explosion combinatoire, precisement ce
# que le benchmark doit illustrer face a alpha-beta).
MINIMAX_DEPTHS = list(range(1, 7))
# Meme avec elagage + tri des coups par le centre, la profondeur 10 fait
# passer une partie complete a plusieurs minutes (~x7 par profondeur
# supplementaire) ; la tendance exponentielle est deja tres claire a 9.
ALPHA_BETA_DEPTHS = list(range(1, 10))
MCTS_SIMULATIONS_PER_DEPTH = 50  # facteur d'echelle simulations ~ profondeur


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
