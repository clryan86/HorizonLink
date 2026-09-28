"""Monte Carlo comparison of uncoded and error-corrected BSC payloads."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from horizonlink.channels.binary_symmetric import transmit as bsc_transmit
from horizonlink.codes.hamming74 import decode as hamming_decode
from horizonlink.codes.hamming74 import encode as hamming_encode
from horizonlink.codes.repetition import decode as repetition_decode
from horizonlink.codes.repetition import encode as repetition_encode


@dataclass(frozen=True)
class ECCBenchmarkResult:
    flip_probability: float
    trials: int
    bits_per_trial: int
    seed: int
    uncoded_mean_ber: float
    uncoded_std_ber: float
    repetition3_mean_ber: float
    repetition3_std_ber: float
    hamming74_mean_ber: float
    hamming74_std_ber: float

    def as_dict(self) -> dict[str, int | float]:
        return {
            "flip_probability": self.flip_probability,
            "trials": self.trials,
            "bits_per_trial": self.bits_per_trial,
            "seed": self.seed,
            "uncoded_code_rate": 1.0,
            "uncoded_mean_ber": self.uncoded_mean_ber,
            "uncoded_std_ber": self.uncoded_std_ber,
            "repetition3_code_rate": 1.0 / 3.0,
            "repetition3_mean_ber": self.repetition3_mean_ber,
            "repetition3_std_ber": self.repetition3_std_ber,
            "hamming74_code_rate": 4.0 / 7.0,
            "hamming74_mean_ber": self.hamming74_mean_ber,
            "hamming74_std_ber": self.hamming74_std_ber,
        }


def _mean_std(values: np.ndarray) -> tuple[float, float]:
    return float(np.mean(values)), float(np.std(values, ddof=0))


def run_ecc_benchmark(
    flip_probability: float,
    *,
    trials: int = 100,
    bits_per_trial: int = 12_000,
    seed: int = 0,
) -> ECCBenchmarkResult:
    """Compare payload BER for uncoded, repetition-3, and Hamming(7,4) links.

    Every scheme experiences the same independent BSC crossover probability per
    transmitted bit. The coded schemes therefore transmit more physical bits;
    their code rates are returned beside BER so reliability is not presented
    without the corresponding redundancy cost.
    """
    flip_probability = float(flip_probability)
    if not np.isfinite(flip_probability) or not 0.0 <= flip_probability <= 1.0:
        raise ValueError("flip_probability must be finite and between 0 and 1")
    if trials <= 0:
        raise ValueError("trials must be positive")
    if bits_per_trial <= 0 or bits_per_trial % 4 != 0:
        raise ValueError("bits_per_trial must be positive and divisible by 4")

    rng = np.random.default_rng(seed)
    uncoded = np.empty(trials, dtype=float)
    repetition = np.empty(trials, dtype=float)
    hamming = np.empty(trials, dtype=float)

    for index in range(trials):
        source = rng.integers(0, 2, size=bits_per_trial, dtype=np.int8)
        seeds = rng.integers(0, np.iinfo(np.int32).max, size=3, dtype=np.int64)

        uncoded_received = bsc_transmit(source, flip_probability, seed=int(seeds[0]))
        repetition_received = bsc_transmit(
            repetition_encode(source, repetitions=3),
            flip_probability,
            seed=int(seeds[1]),
        )
        hamming_received = bsc_transmit(
            hamming_encode(source),
            flip_probability,
            seed=int(seeds[2]),
        )

        uncoded[index] = np.mean(uncoded_received != source)
        repetition[index] = np.mean(
            repetition_decode(repetition_received, repetitions=3) != source
        )
        hamming[index] = np.mean(hamming_decode(hamming_received) != source)

    uncoded_mean, uncoded_std = _mean_std(uncoded)
    repetition_mean, repetition_std = _mean_std(repetition)
    hamming_mean, hamming_std = _mean_std(hamming)
    return ECCBenchmarkResult(
        flip_probability=flip_probability,
        trials=trials,
        bits_per_trial=bits_per_trial,
        seed=seed,
        uncoded_mean_ber=uncoded_mean,
        uncoded_std_ber=uncoded_std,
        repetition3_mean_ber=repetition_mean,
        repetition3_std_ber=repetition_std,
        hamming74_mean_ber=hamming_mean,
        hamming74_std_ber=hamming_std,
    )
