"""Null/permutation tests for candidate discovery scores."""
from __future__ import annotations

import random
from .discovery import scan_pair


def permutation_significance(
    x_name: str,
    y_name: str,
    xs: list[float],
    ys: list[float],
    *,
    model: str = "power_law",
    permutations: int = 200,
    seed: int = 0,
) -> dict:
    """Compare an observed fit score with shuffled-y null fits.

    The returned p-value is empirical and intended as a screening diagnostic,
    not a substitute for physical derivation or independent replication.
    """
    if len(xs) != len(ys) or len(xs) < 8:
        raise ValueError("equal x/y arrays with at least eight points required")
    if permutations < 20:
        raise ValueError("at least 20 permutations required")
    observed = [c for c in scan_pair(x_name, y_name, xs, ys) if c.model == model]
    if not observed:
        raise ValueError(f"model {model!r} is not valid for supplied data")
    observed_score = observed[0].score
    rng = random.Random(seed)
    null_scores = []
    shuffled = list(ys)
    for _ in range(permutations):
        rng.shuffle(shuffled)
        candidates = [c for c in scan_pair(x_name, y_name, xs, shuffled) if c.model == model]
        null_scores.append(candidates[0].score if candidates else -1.0)
    exceed = sum(score >= observed_score for score in null_scores)
    return {
        "x": x_name,
        "y": y_name,
        "model": model,
        "observed_score": observed_score,
        "permutations": permutations,
        "empirical_p_value": (exceed + 1) / (permutations + 1),
        "null_max_score": max(null_scores),
        "interpretation": "permutation screening only; low p does not establish new physics",
    }
