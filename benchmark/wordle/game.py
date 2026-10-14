"""Wordle game rules: feedback computation (green/yellow/gray) for a guess,
with correct handling of duplicate letters (official Wordle algorithm:
two passes, greens first, then yellows on the remaining letters)."""

from __future__ import annotations

GREEN = "G"
YELLOW = "Y"
GRAY = "X"


def get_feedback(guess: str, target: str) -> str:
    if len(guess) != len(target):
        raise ValueError("guess and target must have the same length")

    n = len(target)
    feedback = [GRAY] * n
    target_counts: dict[str, int] = {}

    for i in range(n):
        if guess[i] == target[i]:
            feedback[i] = GREEN
        else:
            target_counts[target[i]] = target_counts.get(target[i], 0) + 1

    for i in range(n):
        if feedback[i] == GREEN:
            continue
        letter = guess[i]
        if target_counts.get(letter, 0) > 0:
            feedback[i] = YELLOW
            target_counts[letter] -= 1

    return "".join(feedback)


def is_win(feedback: str) -> bool:
    return all(c == GREEN for c in feedback)


def filter_candidates(candidates: list[str], guess: str, feedback: str) -> list[str]:
    """Keep only the words compatible with the feedback observed for `guess`."""
    return [word for word in candidates if get_feedback(guess, word) == feedback]
