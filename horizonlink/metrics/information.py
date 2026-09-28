"""Information-theoretic metrics used across experiments."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class BitErrorStats:
    """Counts for a binary transmission with an optional erasure symbol."""

    transmitted: int
    received: int
    erased: int
    errors: int

    @property
    def conditional_ber(self) -> float | None:
        """Error fraction among received bits, or None when every bit was erased."""
        if self.received == 0:
            return None
        return self.errors / self.received

    @property
    def erasure_rate(self) -> float:
        if self.transmitted == 0:
            return 0.0
        return self.erased / self.transmitted


def binary_entropy(p: float) -> float:
    if not math.isfinite(p) or not 0.0 <= p <= 1.0:
        raise ValueError("p must be finite and between 0 and 1")
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


def bit_error_stats(expected, observed, ignore_symbol=-1) -> BitErrorStats:
    """Return explicit error/erasure counts for equal-length binary sequences."""
    expected = list(expected)
    observed = list(observed)
    if len(expected) != len(observed):
        raise ValueError("expected and observed must have equal length")
    if ignore_symbol in (0, 1):
        raise ValueError("ignore_symbol cannot overlap the binary alphabet {0, 1}")
    if any(value not in (0, 1) for value in expected):
        raise ValueError("expected must contain only binary symbols 0 and 1")
    if any(value not in (0, 1, ignore_symbol) for value in observed):
        raise ValueError("observed must contain only 0, 1, or the erasure symbol")

    erased = sum(value == ignore_symbol for value in observed)
    received = len(observed) - erased
    errors = sum(
        expected_value != observed_value
        for expected_value, observed_value in zip(expected, observed, strict=True)
        if observed_value != ignore_symbol
    )
    return BitErrorStats(
        transmitted=len(expected),
        received=received,
        erased=erased,
        errors=errors,
    )


def bit_error_rate(expected, observed, ignore_symbol=-1) -> float | None:
    """Return BER among non-erased bits; None means no bits survived.

    Use :func:`bit_error_stats` when erasure counts and rates are also needed.
    """
    return bit_error_stats(expected, observed, ignore_symbol).conditional_ber
