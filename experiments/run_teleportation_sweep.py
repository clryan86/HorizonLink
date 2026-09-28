"""Sweep Bell-resource Pauli noise and measure teleportation fidelity.

This experiment is a quantum-information analogue. It does not represent a
signal crossing or escaping a classical event horizon.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from horizonlink.protocols.teleportation import teleport
from horizonlink.provenance import experiment_metadata, write_csv_with_metadata
from horizonlink.quantum.states import fidelity_pure, qubit_state

CARDINAL_STATES = [
    (0.0, 0.0),
    (np.pi, 0.0),
    (np.pi / 2.0, 0.0),
    (np.pi / 2.0, np.pi),
    (np.pi / 2.0, np.pi / 2.0),
    (np.pi / 2.0, -np.pi / 2.0),
]


def average_fidelity(error_probability: float) -> float:
    fidelities = []
    for theta, phi in CARDINAL_STATES:
        state = qubit_state(theta, phi)
        output = teleport(state, resource_error_probability=error_probability)
        fidelities.append(fidelity_pure(state, output))
    return float(np.mean(fidelities))


def run(points: int = 41, output_path: str = "results/teleportation_sweep.csv") -> Path:
    if points < 2:
        raise ValueError("points must be at least 2")

    path = Path(output_path)
    probabilities = np.linspace(0.0, 1.0, points)
    rows = [
        {
            "resource_error_probability": float(probability),
            "average_fidelity": average_fidelity(float(probability)),
        }
        for probability in probabilities
    ]
    metadata = experiment_metadata(
        experiment="teleportation-resource-noise-sweep",
        model_level="analogue",
        inputs={
            "points": points,
            "resource_error_min": 0.0,
            "resource_error_max": 1.0,
            "classical_bit_error_probability": 0.0,
            "input_state_ensemble": "six cardinal Bloch-sphere states",
            "pauli_noise_convention": (
                "identity with probability 1-p; X/Y/Z each with probability p/3; "
                "complete depolarization occurs at p=0.75"
            ),
        },
    )
    data_path, _ = write_csv_with_metadata(
        path,
        fieldnames=["resource_error_probability", "average_fidelity"],
        rows=rows,
        metadata=metadata,
    )
    return data_path


def maybe_plot(csv_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    data = np.loadtxt(csv_path, delimiter=",", skiprows=1)
    plt.figure()
    plt.plot(data[:, 0], data[:, 1])
    plt.xlabel("Bell-resource Pauli error probability")
    plt.ylabel("Average teleportation fidelity")
    plt.title("HorizonLink teleportation toy-model sweep")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(csv_path.with_suffix(".png"), dpi=160)
    plt.close()


if __name__ == "__main__":
    result = run()
    maybe_plot(result)
    print(result)
