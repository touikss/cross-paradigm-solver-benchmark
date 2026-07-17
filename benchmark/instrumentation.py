"""Mesure uniforme du temps et de la memoire pour n'importe quel solveur."""

from __future__ import annotations

import time
import tracemalloc
from typing import Callable, TypeVar

from .core import SolverOutput

T = TypeVar("T")


def measure(fn: Callable[[], SolverOutput]) -> tuple[SolverOutput, float, float]:
    """Execute fn() en mesurant temps ecoule (perf_counter) et pic memoire (tracemalloc).

    Retourne (resultat, temps_secondes, memoire_pic_mb).
    """
    tracemalloc.start()
    start = time.perf_counter()
    try:
        result = fn()
    finally:
        elapsed = time.perf_counter() - start
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    peak_mb = peak / (1024 * 1024)
    return result, elapsed, peak_mb
