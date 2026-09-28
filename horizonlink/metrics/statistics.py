"""Small dependency-free statistical summaries for Monte Carlo experiments."""

from __future__ import annotations

import math
from collections.abc import Iterable
from statistics import NormalDist

import numpy as np


def _validate_tolerance(name: str, value: float) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0.0:
        raise ValueError(f"{name} must be finite and non-negative")
    return parsed


def summarize_samples(
    values: Iterable[float],
    confidence: float = 0.95,
    *,
    relative_tolerance: float = 0.05,
    absolute_tolerance: float = 1e-4,
) -> dict[str, float | int | bool | None]:
    """Summarize repeated trial-level measurements and their numerical precision.

    The confidence interval is a normal-approximation interval for the sample
    mean using the sample standard deviation. It is intended as a transparent
    convergence diagnostic, not as a substitute for a domain-specific
    likelihood model.

    ``converged`` reports whether the confidence-interval half-width meets at
    least one requested precision target: an absolute tolerance or a relative
    tolerance with respect to the magnitude of the sample mean. The absolute
    criterion is important for estimates near zero, where relative precision is
    undefined or misleading. With only one trial, uncertainty and convergence
    fields are returned as ``None`` rather than inventing a variance estimate.
    """
    data = np.asarray(list(values), dtype=float)
    if data.ndim != 1 or data.size == 0:
        raise ValueError("values must contain at least one sample")
    if not np.all(np.isfinite(data)):
        raise ValueError("values must all be finite")
    confidence = float(confidence)
    if not math.isfinite(confidence) or not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be finite and between 0 and 1")
    relative_tolerance = _validate_tolerance("relative_tolerance", relative_tolerance)
    absolute_tolerance = _validate_tolerance("absolute_tolerance", absolute_tolerance)

    count = int(data.size)
    mean = float(np.mean(data))
    common: dict[str, float | int | bool | None] = {
        "count": count,
        "mean": mean,
        "confidence": confidence,
        "relative_tolerance": relative_tolerance,
        "absolute_tolerance": absolute_tolerance,
    }
    if count == 1:
        return {
            **common,
            "sample_std": None,
            "standard_error": None,
            "confidence_interval_low": None,
            "confidence_interval_high": None,
            "confidence_interval_half_width": None,
            "relative_standard_error": None,
            "relative_confidence_interval_half_width": None,
            "converged": None,
        }

    sample_std = float(np.std(data, ddof=1))
    standard_error = sample_std / math.sqrt(count)
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    half_width = z * standard_error
    if mean == 0.0:
        relative_standard_error = 0.0 if standard_error == 0.0 else None
        relative_half_width = 0.0 if half_width == 0.0 else None
    else:
        relative_standard_error = standard_error / abs(mean)
        relative_half_width = half_width / abs(mean)

    absolute_precision_met = half_width <= absolute_tolerance
    relative_precision_met = (
        relative_half_width is not None and relative_half_width <= relative_tolerance
    )

    return {
        **common,
        "sample_std": sample_std,
        "standard_error": standard_error,
        "confidence_interval_low": mean - half_width,
        "confidence_interval_high": mean + half_width,
        "confidence_interval_half_width": half_width,
        "relative_standard_error": relative_standard_error,
        "relative_confidence_interval_half_width": relative_half_width,
        "converged": absolute_precision_met or relative_precision_met,
    }
