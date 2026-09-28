"""Monte Carlo helpers for reproducible channel experiments."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from horizonlink.channels.binary_symmetric import transmit as bsc_transmit


@dataclass(frozen=True)
class MonteCarloResult:
    trials: int
    bits_per_trial: int
    flip_probability: float
    mean_bit_error_rate: float
    std_bit_error_rate: float
    seed: int

    def as_dict(self) -> dict[str, int | float]:
        return {
            "trials": self.trials,
            "bits_per_trial": self.bits_per_trial,
            "flip_probability": self.flip_probability,
            "mean_bit_error_rate": self.mean_bit_error_rate,
            "std_bit_error_rate": self.std_bit_error_rate,
            "seed": self.seed,
        }


def run_bsc_trials(
    flip_probability: float,
    *,
    trials: int = 100,
    bits_per_trial: int = 10_000,
    seed: int = 0,
) -> MonteCarloResult:
    """Estimate bit-error rate statistics for a binary symmetric channel."""
    if not 0.0 <= flip_probability <= 1.0:
        raise ValueError("flip_probability must be between 0 and 1")
    if trials <= 0 or bits_per_trial <= 0:
        raise ValueError("trials and bits_per_trial must be positive")

    rng = np.random.default_rng(seed)
    error_rates = np.empty(trials, dtype=float)

    for index in range(trials):
        bits = rng.integers(0, 2, size=bits_per_trial, dtype=np.int8)
        trial_seed = int(rng.integers(0, np.iinfo(np.int32).max))
        received = bsc_transmit(bits, flip_probability, seed=trial_seed)
        error_rates[index] = np.mean(received != bits)

    return MonteCarloResult(
        trials=trials,
        bits_per_trial=bits_per_trial,
        flip_probability=flip_probability,
        mean_bit_error_rate=float(np.mean(error_rates)),
        std_bit_error_rate=float(np.std(error_rates, ddof=0)),
        seed=seed,
    )
