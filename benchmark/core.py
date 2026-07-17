"""Modele de donnees commun et orchestration du benchmark cross-paradigme."""

from __future__ import annotations

import os
import resource
import signal
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
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


class InstanceTimeout(Exception):
    pass


@contextmanager
def _time_limit(seconds: float):
    """Interrompt le bloc via SIGALRM si depasse `seconds`. Fonctionne dans le
    thread principal de n'importe quel processus (y compris un worker separe
    lance par ProcessPoolExecutor, qui a son propre thread principal).
    N'interrompt pas un appel C bloquant qui ne rend jamais la main a
    l'interpreteur (non pertinent ici : les solveurs lents sont en pur Python)."""

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
    """Execute un solveur sur une instance avec mesure temps/memoire et budget
    de temps. Fonction top-level (picklable) pour pouvoir tourner dans un
    worker de ProcessPoolExecutor.

    La memoire est mesuree via ru_maxrss (pic memoire du processus, en Ko)
    plutot que tracemalloc : tracemalloc trace chaque allocation individuelle
    et ralentit d'un facteur 4-10x les solveurs qui allouent beaucoup (GA,
    recuit simule), ce qui faussait les mesures de temps. ru_maxrss est
    quasi gratuit et, comme chaque worker ne traite qu'une instance, il
    approxime bien le pic memoire de ce solve.
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
    """Execute un solveur sequentiellement sur une liste d'instances.

    instances: iterable de (instance_id, difficulty, instance_data)
    timeout_seconds: si une instance depasse ce budget, elle est comptee en
        echec (timeout) et on passe a la suivante plutot que de bloquer tout
        le benchmark.
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
    """Comme run_benchmark, mais distribue les instances sur plusieurs processus
    (les instances d'un meme solveur sont independantes). Le budget de temps
    est applique dans chaque worker via SIGALRM : une instance qui depasse le
    budget s'auto-interrompt et libere son worker pour la tache suivante.

    `solver` doit etre une fonction top-level (picklable) - pas de lambda ni
    de closure retournee par une factory.
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
