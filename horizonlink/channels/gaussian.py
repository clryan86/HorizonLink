"""Simple additive white Gaussian noise channel helpers."""

from __future__ import annotations

import math

_LN2 = math.log(2.0)
_LN10_OVER_10 = math.log(10.0) / 10.0


def capacity_from_snr(snr_linear: float, bandwidth_hz: float = 1.0) -> float:
    """Shannon-Hartley capacity in bits/s for an ideal AWGN channel."""
    snr_linear = float(snr_linear)
    bandwidth_hz = float(bandwidth_hz)
    if not math.isfinite(snr_linear) or snr_linear < 0.0:
        raise ValueError("snr_linear must be finite and non-negative")
    if not math.isfinite(bandwidth_hz) or bandwidth_hz <= 0.0:
        raise ValueError("bandwidth_hz must be finite and positive")
    return bandwidth_hz * math.log1p(snr_linear) / _LN2


def capacity_from_snr_db(snr_db: float, bandwidth_hz: float = 1.0) -> float:
    """Stable Shannon-Hartley capacity directly from power SNR in dB."""
    snr_db = float(snr_db)
    bandwidth_hz = float(bandwidth_hz)
    if not math.isfinite(snr_db):
        raise ValueError("snr_db must be finite")
    if not math.isfinite(bandwidth_hz) or bandwidth_hz <= 0.0:
        raise ValueError("bandwidth_hz must be finite and positive")

    x = snr_db * _LN10_OVER_10
    # Stable softplus: log(1 + exp(x)) without overflowing exp(x).
    softplus = x + math.log1p(math.exp(-x)) if x > 0.0 else math.log1p(math.exp(x))
    return bandwidth_hz * softplus / _LN2


def snr_db_to_linear(snr_db: float) -> float:
    """Convert finite power SNR in dB to linear form when representable."""
    snr_db = float(snr_db)
    if not math.isfinite(snr_db):
        raise ValueError("snr_db must be finite")
    exponent = snr_db * _LN10_OVER_10
    if exponent > math.log(float.fromhex("0x1.fffffffffffffp+1023")):
        raise OverflowError("linear SNR exceeds floating-point range; use capacity_from_snr_db")
    return math.exp(exponent)
