"""Small dependency-free grid-search helper."""

from __future__ import annotations

from itertools import product


def maximize(objective, parameter_grid: dict):
    """Return (best_params, best_score) over a Cartesian product grid."""
    if not parameter_grid:
        raise ValueError("parameter_grid cannot be empty")
    keys = list(parameter_grid)
    values = [list(parameter_grid[k]) for k in keys]
    if any(not v for v in values):
        raise ValueError("each parameter must have at least one candidate")

    best_params = None
    best_score = None
    for combo in product(*values):
        params = dict(zip(keys, combo))
        score = objective(**params)
        if best_score is None or score > best_score:
            best_params, best_score = params, score
    return best_params, best_score
