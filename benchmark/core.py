"""Modele de donnees commun et orchestration du benchmark cross-paradigme."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Iterable

import pandas as pd


@dataclass
class SolverOutput:
    """Resultat brut retourne par un solveur, avant mesure temps/memoire."""

    success: bool
    nodes_explored: int
    solution_quality: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Metrics:
    """Une ligne de resultat de benchmark, uniforme quel que soit le jeu/paradigme."""

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
    """Compteur de 'noeuds explores' incremente par un solveur pendant sa recherche.

    La notion de noeud varie par famille de paradigme (voir README/notebook) :
    decision/affectation testee (backtracking, DLX, CP-SAT, SMT), noeud de l'arbre
    de jeu visite (minimax, alpha-beta, MCTS), evaluation de fitness (GA, recuit
    simule), ou mot candidat evalue (Wordle). Ce compteur ne fait qu'incrementer ;
    la semantique est documentee au niveau de chaque solveur.
    """

    def __init__(self) -> None:
        self.count = 0

    def increment(self, n: int = 1) -> None:
        self.count += n


def run_benchmark(
    game: str,
    paradigm: str,
    solver: Solver,
    instances: Iterable[tuple[str, str | int, Any]],
    measure_fn: Callable[[Callable[[], SolverOutput]], tuple[SolverOutput, float, float]],
) -> list[Metrics]:
    """Execute un solveur sur une liste d'instances et retourne les metriques.

    instances: iterable de (instance_id, difficulty, instance_data)
    measure_fn: wrapper de mesure (voir instrumentation.measure) qui execute le
        callable passe et retourne (SolverOutput, temps_secondes, memoire_pic_mb)
    """
    results: list[Metrics] = []
    for instance_id, difficulty, instance_data in instances:
        counter = NodeCounter()
        output, elapsed, peak_mem = measure_fn(lambda: solver(instance_data, counter))
        results.append(
            Metrics(
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
        )
    return results


def metrics_to_dataframe(metrics: Iterable[Metrics]) -> pd.DataFrame:
    return pd.DataFrame([m.to_row() for m in metrics])
