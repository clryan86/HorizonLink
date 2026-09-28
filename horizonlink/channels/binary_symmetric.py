"""Binary symmetric channel (BSC) helpers.

The BSC is a deliberately simple information-theory baseline: each bit is
independently flipped with probability p. It is useful for comparing toy
horizon-channel models against a familiar noisy-channel reference.
"""

from __future__ import annotations

import math

import numpy as np


def binary_entropy(probability: float) -> float:
    """Return the binary entropy H2(p) in bits."""
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be between 0 and 1")
    if probability in (0.0, 1.0):
        return 0.0
    p = probability
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def capacity_bits_per_use(flip_probability: float) -> float:
    """Shannon capacity of a BSC in bits per channel use."""
    if not 0.0 <= flip_probability <= 0.5:
        raise ValueError("flip_probability must be between 0 and 0.5")
    return 1.0 - binary_entropy(flip_probability)


def transmit(bits, flip_probability: float, seed: int | None = None) -> np.ndarray:
    """Transmit a 0/1 sequence through an independent bit-flip channel."""
    if not 0.0 <= flip_probability <= 1.0:
        raise ValueError("flip_probability must be between 0 and 1")
    data = np.asarray(bits, dtype=np.int8)
    if data.ndim != 1 or np.any((data != 0) & (data != 1)):
        raise ValueError("bits must be a one-dimensional sequence of 0s and 1s")
    rng = np.random.default_rng(seed)
    flips = rng.random(data.size) < flip_probability
    return np.bitwise_xor(data, flips.astype(np.int8))
