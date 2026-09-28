"""Information-theoretic metrics used across experiments."""

from __future__ import annotations

import math
from collections import Counter


def binary_entropy(p: float) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be between 0 and 1")
    if p in (0.0, 1.0):
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


def shannon_entropy(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    counts = Counter(values)
    n = len(values)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def bit_error_rate(expected, observed, ignore_symbol=-1) -> float:
    pairs = [(a, b) for a, b in zip(expected, observed) if b != ignore_symbol]
    if not pairs:
        return 0.0
    return sum(a != b for a, b in pairs) / len(pairs)
