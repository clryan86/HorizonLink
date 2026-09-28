"""Small dependency-free statistical summaries for Monte Carlo experiments."""

from __future__ import annotations

import math
from collections.abc import Iterable
from statistics import NormalDist

import numpy as np


def summarize_samples(values: Iterable[float], confidence: float = 0.95) -> dict[str, float | int | None]:
    """Summarize repeated trial-level measurements.

    The confidence interval is a normal-approximation interval for the sample
    mean using the sample standard deviation. It is intended as a transparent
    convergence diagnostic, not as a substitute for a domain-specific
    likelihood model. With only one trial, uncertainty fields are returned as
    ``None`` rather than inventing a variance estimate.
    """
    data = np.asarray(list(values), dtype=float)
    if data.ndim != 1 or data.size == 0:
        raise ValueError("values must contain at least one sample")
    if not np.all(np.isfinite(data)):
        raise ValueError("values must all be finite")
    confidence = float(confidence)
    if not math.isfinite(confidence) or not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be finite and between 0 and 1")

    count = int(data.size)
    mean = float(np.mean(data))
    if count == 1:
        return {
            "count": count,
            "mean": mean,
            "sample_std": None,
            "standard_error": None,
            "confidence": confidence,
            "confidence_interval_low": None,
            "confidence_interval_high": None,
            "relative_standard_error": None,
        }

    sample_std = float(np.std(data, ddof=1))
    standard_error = sample_std / math.sqrt(count)
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    margin = z * standard_error
    if mean == 0.0:
        relative_standard_error = 0.0 if standard_error == 0.0 else None
    else:
        relative_standard_error = standard_error / abs(mean)

    return {
        "count": count,
        "mean": mean,
        "sample_std": sample_std,
        "standard_error": standard_error,
        "confidence": confidence,
        "confidence_interval_low": mean - margin,
        "confidence_interval_high": mean + margin,
        "relative_standard_error": relative_standard_error,
    }
