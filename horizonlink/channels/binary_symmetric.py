"""Binary symmetric channel (BSC) helpers.

The BSC is a deliberately simple information-theory baseline: each bit is
independently flipped with probability p. It is useful for comparing toy
horizon-channel models against a familiar noisy-channel reference.
"""

from __future__ import annotations

import math

import numpy as np

from horizonlink.metrics.information import binary_entropy


def _probability(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return value


def capacity_bits_per_use(flip_probability: float) -> float:
    """Shannon capacity of a BSC in bits per channel use.

    The full physical interval ``0 <= p <= 1`` is supported. Capacity is
    symmetric because a deterministic/mostly deterministic flip can be inverted:
    ``C(p) = C(1-p)``.
    """
    flip_probability = _probability("flip_probability", flip_probability)
    return 1.0 - binary_entropy(flip_probability)


def transmit(bits, flip_probability: float, seed: int | None = None) -> np.ndarray:
    """Transmit a one-dimensional 0/1 sequence through an independent bit-flip channel."""
    flip_probability = _probability("flip_probability", flip_probability)
    raw = np.asarray(bits)
    if raw.ndim != 1:
        raise ValueError("bits must be a one-dimensional sequence of 0s and 1s")
    if not np.all((raw == 0) | (raw == 1)):
        raise ValueError("bits must contain only the exact binary symbols 0 and 1")
    data = raw.astype(np.int8, copy=False)
    rng = np.random.default_rng(seed)
    flips = rng.random(data.size) < flip_probability
    return np.bitwise_xor(data, flips.astype(np.int8))
