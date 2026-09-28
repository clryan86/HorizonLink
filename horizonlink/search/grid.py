"""Small dependency-free grid-search helper."""

from __future__ import annotations

import math
from itertools import product
from numbers import Real


def maximize(objective, parameter_grid: dict):
    """Return ``(best_params, best_score)`` over a Cartesian product grid.

    Objective values must be finite real scalars. A failed/non-finite candidate
    raises immediately with the offending parameters instead of being allowed to
    become a misleading optimum.
    """
    if not parameter_grid:
        raise ValueError("parameter_grid cannot be empty")
    keys = list(parameter_grid)
    values = [list(parameter_grid[k]) for k in keys]
    if any(not value_list for value_list in values):
        raise ValueError("each parameter must have at least one candidate")

    best_params = None
    best_score = None
    for combo in product(*values):
        params = dict(zip(keys, combo, strict=True))
        score = objective(**params)
        if isinstance(score, bool) or not isinstance(score, Real):
            raise TypeError(f"objective must return a real scalar; got {score!r} for {params!r}")
        score = float(score)
        if not math.isfinite(score):
            raise ValueError(f"objective returned non-finite score {score!r} for {params!r}")
        if best_score is None or score > best_score:
            best_params, best_score = params, score

    return best_params, best_score
