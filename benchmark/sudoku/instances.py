from __future__ import annotations

import random
from pathlib import Path

from .grid import SudokuGrid

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "sudoku"

DIFFICULTY_FILES = {
    "easy": "easy51.txt",
    "medium_hard": "top95.txt",
    "diabolical": "hardest11.txt",
}


def load_puzzles(difficulty: str) -> list[str]:
    path = DATA_DIR / DIFFICULTY_FILES[difficulty]
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    return lines


def sample_instances(
    n_per_difficulty: int = 10, seed: int = 42
) -> list[tuple[str, str, SudokuGrid]]:
    """Retourne (instance_id, difficulty, grille) pour un echantillon par difficulte."""
    rng = random.Random(seed)
    instances: list[tuple[str, str, SudokuGrid]] = []
    for difficulty in DIFFICULTY_FILES:
        puzzles = load_puzzles(difficulty)
        sample = rng.sample(puzzles, min(n_per_difficulty, len(puzzles)))
        for i, puzzle_str in enumerate(sample):
            instance_id = f"{difficulty}_{i}"
            instances.append((instance_id, difficulty, SudokuGrid.from_string(puzzle_str)))
    return instances
