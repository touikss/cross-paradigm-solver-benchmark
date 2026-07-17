"""Monte Carlo Tree Search (selection UCB1, rollout aleatoire).

Un 'noeud explore' = une simulation MCTS (selection+expansion+rollout+backprop).
Contrairement a minimax/alpha-beta, MCTS n'a pas de profondeur fixe : le budget
est donne en nombre de simulations (anytime), a comparer en cout temps avec
les paradigmes a profondeur fixe (voir discussion dans le notebook).
"""

from __future__ import annotations

import math
import random

from ..core import NodeCounter, SolverOutput
from .board import Board
from .match import run_match_solver

EXPLORATION_CONSTANT = 1.4


class MCTSNode:
    def __init__(self, board: Board, parent: "MCTSNode | None" = None, move: int | None = None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children: list[MCTSNode] = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = board.legal_moves()

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def best_child(self) -> "MCTSNode":
        def ucb1(node: "MCTSNode") -> float:
            exploitation = node.wins / node.visits
            exploration = EXPLORATION_CONSTANT * math.sqrt(math.log(self.visits) / node.visits)
            return exploitation + exploration

        return max(self.children, key=ucb1)

    def expand(self, rng: random.Random) -> "MCTSNode":
        move = self.untried_moves.pop(rng.randrange(len(self.untried_moves)))
        child = MCTSNode(self.board.play(move), parent=self, move=move)
        self.children.append(child)
        return child


def _rollout(board: Board, player: int, rng: random.Random) -> float:
    current = board
    while not current.is_terminal():
        move = rng.choice(current.legal_moves())
        current = current.play(move)
    winner = current.winner()
    if winner is None:
        return 0.5
    return 1.0 if winner == player else 0.0


def search(root_board: Board, n_simulations: int, counter: NodeCounter, seed: int = 0) -> int:
    rng = random.Random(seed)
    player = root_board.to_move
    root = MCTSNode(root_board)

    for _ in range(n_simulations):
        counter.increment()
        node = root
        while node.is_fully_expanded() and node.children and not node.board.is_terminal():
            node = node.best_child()

        if not node.board.is_terminal() and not node.is_fully_expanded():
            node = node.expand(rng)

        result = _rollout(node.board, player, rng)

        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    return max(root.children, key=lambda n: n.visits).move


def solve_mcts(instance: tuple[Board, int], counter: NodeCounter) -> SolverOutput:
    board, n_simulations = instance

    def agent_choose_move(b: Board, c: NodeCounter) -> int:
        return search(b, n_simulations, c)

    return run_match_solver(agent_choose_move, board, counter)
