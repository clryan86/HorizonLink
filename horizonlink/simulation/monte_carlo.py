"""Monte Carlo helpers for reproducible channel experiments."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from horizonlink.channels.binary_symmetric import transmit as bsc_transmit
from horizonlink.metrics.statistics import summarize_samples


@dataclass(frozen=True)
class MonteCarloResult:
    trials: int
    bits_per_trial: int
    flip_probability: float
    mean_bit_error_rate: float
    std_bit_error_rate: float
    standard_error: float | None
    confidence: float
    confidence_interval_low: float | None
    confidence_interval_high: float | None
    relative_standard_error: float | None
    seed: int

    def as_dict(self) -> dict[str, int | float | None]:
        return {
            "trials": self.trials,
            "bits_per_trial": self.bits_per_trial,
            "flip_probability": self.flip_probability,
            "mean_bit_error_rate": self.mean_bit_error_rate,
            "std_bit_error_rate": self.std_bit_error_rate,
            "standard_error": self.standard_error,
            "confidence": self.confidence,
            "confidence_interval_low": self.confidence_interval_low,
            "confidence_interval_high": self.confidence_interval_high,
            "relative_standard_error": self.relative_standard_error,
            "seed": self.seed,
        }


def run_bsc_trials(
    flip_probability: float,
    *,
    trials: int = 100,
    bits_per_trial: int = 10_000,
    seed: int = 0,
    confidence: float = 0.95,
) -> MonteCarloResult:
    """Estimate BSC BER with reproducible trial-level convergence diagnostics."""
    flip_probability = float(flip_probability)
    if not np.isfinite(flip_probability) or not 0.0 <= flip_probability <= 1.0:
        raise ValueError("flip_probability must be finite and between 0 and 1")
    if trials <= 0 or bits_per_trial <= 0:
        raise ValueError("trials and bits_per_trial must be positive")

    rng = np.random.default_rng(seed)
    error_rates = np.empty(trials, dtype=float)

    for index in range(trials):
        bits = rng.integers(0, 2, size=bits_per_trial, dtype=np.int8)
        trial_seed = int(rng.integers(0, np.iinfo(np.int32).max))
        received = bsc_transmit(bits, flip_probability, seed=trial_seed)
        error_rates[index] = np.mean(received != bits)

    summary = summarize_samples(error_rates, confidence=confidence)
    return MonteCarloResult(
        trials=trials,
        bits_per_trial=bits_per_trial,
        flip_probability=flip_probability,
        mean_bit_error_rate=float(summary["mean"]),
        std_bit_error_rate=float(np.std(error_rates, ddof=0)),
        standard_error=summary["standard_error"],
        confidence=float(summary["confidence"]),
        confidence_interval_low=summary["confidence_interval_low"],
        confidence_interval_high=summary["confidence_interval_high"],
        relative_standard_error=summary["relative_standard_error"],
        seed=seed,
    )
