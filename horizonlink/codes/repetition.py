"""Odd-length repetition code with majority-vote decoding."""

from __future__ import annotations

import numpy as np


def _validated_bits(bits) -> np.ndarray:
    data = np.asarray(bits, dtype=np.int8)
    if data.ndim != 1 or np.any((data != 0) & (data != 1)):
        raise ValueError("bits must be a one-dimensional sequence of 0s and 1s")
    return data


def _validated_repetitions(repetitions: int) -> int:
    repetitions = int(repetitions)
    if repetitions <= 0 or repetitions % 2 == 0:
        raise ValueError("repetitions must be a positive odd integer")
    return repetitions


def encode(bits, repetitions: int = 3) -> np.ndarray:
    """Repeat every source bit an odd number of times."""
    data = _validated_bits(bits)
    repetitions = _validated_repetitions(repetitions)
    return np.repeat(data, repetitions)


def decode(encoded_bits, repetitions: int = 3) -> np.ndarray:
    """Decode repetition-coded bits by majority vote."""
    encoded = _validated_bits(encoded_bits)
    repetitions = _validated_repetitions(repetitions)
    if encoded.size % repetitions != 0:
        raise ValueError("encoded bit count must be divisible by repetitions")
    if encoded.size == 0:
        return encoded.copy()
    blocks = encoded.reshape(-1, repetitions)
    votes = np.sum(blocks, axis=1)
    return (votes > repetitions // 2).astype(np.int8)
