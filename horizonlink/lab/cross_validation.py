"""Out-of-sample validation for candidate numerical relationships.

Candidates are hypotheses. A high in-sample fit is insufficient; this module
scores whether the same fitted form predicts held-out points.
"""
from __future__ import annotations

import math
from .discovery import scan_pair


def _predict(candidate, x: float) -> float:
    p = candidate.parameters
    if candidate.model == "linear":
        return p["intercept"] + p["slope"] * x
    if candidate.model == "power_law":
        if x <= 0:
            raise ValueError("power-law validation requires positive x")
        return p["coefficient"] * x ** p["exponent"]
    if candidate.model == "logarithmic":
        if x <= 0:
            raise ValueError("logarithmic validation requires positive x")
        return p["intercept"] + p["log_slope"] * math.log(x)
    raise ValueError(f"unsupported model: {candidate.model}")


def validate_pair(
    x_name: str,
    y_name: str,
    xs: list[float],
    ys: list[float],
    *,
    holdout_stride: int = 4,
) -> list[dict]:
    """Fit on non-holdout points and report normalized held-out error."""
    if len(xs) != len(ys) or len(xs) < 8:
        raise ValueError("equal x/y arrays with at least eight points required")
    if holdout_stride < 2:
        raise ValueError("holdout_stride must be >= 2")
    train = [(x, y) for i, (x, y) in enumerate(zip(xs, ys)) if i % holdout_stride]
    test = [(x, y) for i, (x, y) in enumerate(zip(xs, ys)) if not i % holdout_stride]
    candidates = scan_pair(x_name, y_name, [x for x, _ in train], [y for _, y in train])
    scale = max(abs(float(y)) for y in ys) or 1.0
    results = []
    for candidate in candidates:
        errors = []
        try:
            for x, y in test:
                errors.append(abs(_predict(candidate, float(x)) - float(y)) / scale)
        except (ValueError, OverflowError):
            continue
        rmse = math.sqrt(sum(e * e for e in errors) / len(errors))
        results.append({
            "x": x_name,
            "y": y_name,
            "model": candidate.model,
            "training_score": candidate.score,
            "holdout_nrmse": rmse,
            "holdout_points": len(test),
            "parameters": candidate.parameters,
            "passes_1pct": rmse <= 0.01,
            "interpretation": "out-of-sample numerical validation; not proof of a physical law",
        })
    return sorted(results, key=lambda item: item["holdout_nrmse"])
