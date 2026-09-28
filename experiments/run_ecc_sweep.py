"""Sweep BSC flip probability and compare uncoded versus coded payload BER."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from horizonlink.provenance import experiment_metadata, write_csv_with_metadata
from horizonlink.simulation.ecc_benchmark import run_ecc_benchmark


def run(
    *,
    points: int = 21,
    max_flip_probability: float = 0.2,
    trials: int = 50,
    bits_per_trial: int = 12_000,
    seed: int = 0,
    confidence: float = 0.95,
    output_path: str = "results/ecc_sweep.csv",
) -> Path:
    if points < 2:
        raise ValueError("points must be at least 2")
    if not np.isfinite(max_flip_probability) or not 0.0 < max_flip_probability <= 1.0:
        raise ValueError("max_flip_probability must be finite and in (0, 1]")
    if not np.isfinite(confidence) or not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be finite and between 0 and 1")

    probabilities = np.linspace(0.0, max_flip_probability, points)
    rows = []
    for index, probability in enumerate(probabilities):
        result = run_ecc_benchmark(
            float(probability),
            trials=trials,
            bits_per_trial=bits_per_trial,
            seed=seed + index,
            confidence=confidence,
        ).as_dict()
        rows.append(result)

    metadata = experiment_metadata(
        experiment="bsc-error-correction-sweep",
        model_level="analogue",
        inputs={
            "points": points,
            "max_flip_probability": max_flip_probability,
            "trials_per_point": trials,
            "bits_per_trial": bits_per_trial,
            "seed": seed,
            "confidence": confidence,
            "confidence_method": (
                "normal-approximation interval for the trial-level mean using sample standard "
                "deviation; intended as a convergence diagnostic"
            ),
            "schemes": ["uncoded", "repetition-3", "hamming-7-4"],
            "comparison_basis": (
                "same independent BSC flip probability per transmitted physical bit; "
                "coded schemes consume additional transmitted bits"
            ),
        },
        seed=seed,
    )
    path, _ = write_csv_with_metadata(
        Path(output_path),
        fieldnames=list(rows[0]),
        rows=rows,
        metadata=metadata,
    )
    return path


def maybe_plot(csv_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    data = np.genfromtxt(csv_path, delimiter=",", names=True)
    plt.figure()
    plt.plot(data["flip_probability"], data["uncoded_mean_ber"], label="Uncoded")
    plt.plot(data["flip_probability"], data["repetition3_mean_ber"], label="Repetition-3")
    plt.plot(data["flip_probability"], data["hamming74_mean_ber"], label="Hamming(7,4)")
    plt.xlabel("BSC flip probability")
    plt.ylabel("Mean payload bit error rate")
    plt.title("HorizonLink error-correction benchmark")
    plt.legend()
    plt.tight_layout()
    plt.savefig(csv_path.with_suffix(".png"), dpi=170)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--points", type=int, default=21)
    parser.add_argument("--max-flip-probability", type=float, default=0.2)
    parser.add_argument("--trials", type=int, default=50)
    parser.add_argument("--bits", type=int, default=12_000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--output", type=Path, default=Path("results/ecc_sweep.csv"))
    args = parser.parse_args()

    result = run(
        points=args.points,
        max_flip_probability=args.max_flip_probability,
        trials=args.trials,
        bits_per_trial=args.bits,
        seed=args.seed,
        confidence=args.confidence,
        output_path=str(args.output),
    )
    maybe_plot(result)
    print(result)


if __name__ == "__main__":
    main()
