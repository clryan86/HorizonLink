"""Simple additive white Gaussian noise channel helpers."""

from __future__ import annotations

import math


def capacity_from_snr(snr_linear: float, bandwidth_hz: float = 1.0) -> float:
    """Shannon-Hartley capacity in bits/s for an ideal AWGN channel."""
    if snr_linear < 0:
        raise ValueError("snr_linear must be non-negative")
    if bandwidth_hz <= 0:
        raise ValueError("bandwidth_hz must be positive")
    return bandwidth_hz * math.log2(1.0 + snr_linear)


def snr_db_to_linear(snr_db: float) -> float:
    return 10.0 ** (snr_db / 10.0)
