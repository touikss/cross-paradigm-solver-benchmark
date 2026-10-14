"""Diagnose why alpha-beta at depth 9 loses against the depth-4 reference.

Plays alpha-beta at several depths against alpha-beta references of depth
3, 4 and 5, as first AND second player, reusing the repo's ``play_match``
and ``choose_move``. Nothing is written to ``results/``.

Usage:
    uv run python scripts/diagnose_alpha_beta_depth9.py            # depth 9 vs 3/4/5
    uv run python scripts/diagnose_alpha_beta_depth9.py --context  # also depths 7, 8, 10 vs 4

A depth-9 game costs roughly 70 s; depth 10 several minutes.
"""

from __future__ import annotations

import argparse
import time

from benchmark.connect_four import alpha_beta, match
from benchmark.connect_four.board import PLAYER_1, PLAYER_2, Board
from benchmark.core import NodeCounter


def play_game(agent_depth: int, reference_depth: int, agent_plays: int) -> dict:
    """Play one full game; the reference depth is injected into the repo's
    reference player by patching ``match._reference_choose_move``."""

    def reference(board: Board, _counter: NodeCounter) -> int:
        return alpha_beta.choose_move(board, reference_depth, NodeCounter())

    def agent(board: Board, counter: NodeCounter) -> int:
        return alpha_beta.choose_move(board, agent_depth, counter)

    original = match._reference_choose_move
    match._reference_choose_move = reference
    try:
        counter = NodeCounter()
        start = time.perf_counter()
        winner, plies = match.play_match(agent, Board(), counter, agent_plays=agent_plays)
        elapsed = time.perf_counter() - start
    finally:
        match._reference_choose_move = original

    if winner is None:
        result = "draw"
    elif winner == agent_plays:
        result = "agent"
    else:
        result = "reference"
    return {"result": result, "plies": plies, "nodes": counter.count, "time": elapsed}


def report(agent_depth: int, reference_depth: int, side: int) -> None:
    out = play_game(agent_depth, reference_depth, side)
    side_name = "first" if side == PLAYER_1 else "second"
    print(
        f"agent d={agent_depth:<2} ref d={reference_depth} side={side_name:<6} "
        f"winner={out['result']:<9} plies={out['plies']:<3} "
        f"agent_nodes={out['nodes']:<8} time={out['time']:.1f}s",
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--context", action="store_true", help="also play depths 7, 8, 10 vs 4")
    args = parser.parse_args()

    for ref in (3, 4, 5):
        for side in (PLAYER_1, PLAYER_2):
            report(9, ref, side)
    if args.context:
        for depth in (7, 8, 10):
            report(depth, 4, PLAYER_1)


if __name__ == "__main__":
    main()
