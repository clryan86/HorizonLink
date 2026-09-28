"""Binary erasure-channel models."""

from __future__ import annotations

import numpy as np


def capacity(erasure_probability: float) -> float:
    """Return Shannon capacity (bits/use) of a binary erasure channel."""
    if not 0.0 <= erasure_probability <= 1.0:
        raise ValueError("erasure_probability must be between 0 and 1")
    return 1.0 - erasure_probability


def transmit(bits, erasure_probability: float, rng=None) -> np.ndarray:
    """Transmit 0/1 bits; erased symbols are returned as -1."""
    if not 0.0 <= erasure_probability <= 1.0:
        raise ValueError("erasure_probability must be between 0 and 1")
    arr = np.asarray(bits, dtype=int)
    if np.any((arr != 0) & (arr != 1)):
        raise ValueError("bits must contain only 0 and 1")
    rng = np.random.default_rng(rng)
    out = arr.copy()
    out[rng.random(arr.shape) < erasure_probability] = -1
    return out
