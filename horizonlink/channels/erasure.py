"""Binary erasure-channel models."""

from __future__ import annotations

import math

import numpy as np


def _probability(value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("erasure_probability must be finite and between 0 and 1")
    return value


def capacity(erasure_probability: float) -> float:
    """Return Shannon capacity (bits/use) of a binary erasure channel."""
    erasure_probability = _probability(erasure_probability)
    return 1.0 - erasure_probability


def transmit(bits, erasure_probability: float, rng=None) -> np.ndarray:
    """Transmit a one-dimensional 0/1 sequence; erased symbols are returned as -1."""
    erasure_probability = _probability(erasure_probability)
    raw = np.asarray(bits)
    if raw.ndim != 1:
        raise ValueError("bits must be a one-dimensional sequence of 0s and 1s")
    if not np.all((raw == 0) | (raw == 1)):
        raise ValueError("bits must contain only the exact binary symbols 0 and 1")
    arr = raw.astype(int, copy=False)
    generator = np.random.default_rng(rng)
    out = arr.copy()
    out[generator.random(arr.shape) < erasure_probability] = -1
    return out
