from __future__ import annotations

import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "wordle"

LENGTHS = [5, 6, 7, 8]
MAX_ATTEMPTS = 6


def load_words(length: int) -> list[str]:
    path = DATA_DIR / f"words{length}.txt"
    return [w.strip() for w in path.read_text().splitlines() if w.strip()]


def sample_instances(
    n_per_length: int = 10, seed: int = 42
) -> list[tuple[str, int, tuple[str, list[str]]]]:
    """Retourne (instance_id, longueur, (mot_cible, liste_de_candidats))."""
    rng = random.Random(seed)
    instances = []
    for length in LENGTHS:
        words = load_words(length)
        targets = rng.sample(words, min(n_per_length, len(words)))
        for i, target in enumerate(targets):
            instance_id = f"len{length}_{i}"
            instances.append((instance_id, length, (target, words)))
    return instances
