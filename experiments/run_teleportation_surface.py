"""Map teleportation fidelity over quantum-resource and classical-channel noise.

The experiment writes a CSV grid. It is a standard quantum-information toy
model and does not represent communication through a classical event horizon.
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


def average_fidelity(resource_error: float, classical_bit_error: float) -> float:
    values = []
    for theta, phi in CARDINAL_STATES:
        state = qubit_state(theta, phi)
        output = teleport(
            state,
            resource_error_probability=resource_error,
            classical_bit_error_probability=classical_bit_error,
        )
        values.append(fidelity_pure(state, output))
    return float(np.mean(values))


def run(
    *,
    resource_points: int = 21,
    classical_points: int = 21,
    output_path: str = "results/teleportation_surface.csv",
) -> Path:
    if resource_points < 2 or classical_points < 2:
        raise ValueError("both grid dimensions must contain at least two points")

    path = Path(output_path)
    resource_values = np.linspace(0.0, 1.0, resource_points)
    classical_values = np.linspace(0.0, 0.5, classical_points)

    rows = []
    for resource_error in resource_values:
        for classical_error in classical_values:
            rows.append(
                {
                    "resource_error_probability": float(resource_error),
                    "classical_bit_error_probability": float(classical_error),
                    "average_fidelity": average_fidelity(
                        float(resource_error), float(classical_error)
                    ),
                }
            )

    metadata = experiment_metadata(
        experiment="teleportation-quantum-classical-noise-surface",
        model_level="analogue",
        inputs={
            "resource_points": resource_points,
            "classical_points": classical_points,
            "resource_error_min": 0.0,
            "resource_error_max": 1.0,
            "classical_bit_error_min": 0.0,
            "classical_bit_error_max": 0.5,
            "input_state_ensemble": "six cardinal Bloch-sphere states",
            "pauli_noise_convention": (
                "identity with probability 1-p; X/Y/Z each with probability p/3; "
                "complete depolarization occurs at p=0.75"
            ),
        },
    )
    data_path, _ = write_csv_with_metadata(
        path,
        fieldnames=[
            "resource_error_probability",
            "classical_bit_error_probability",
            "average_fidelity",
        ],
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
    resource = data[:, 0]
    classical = data[:, 1]
    fidelity = data[:, 2]

    plt.figure()
    contour = plt.tricontourf(resource, classical, fidelity, levels=20)
    plt.xlabel("Bell-resource Pauli error probability")
    plt.ylabel("Classical correction-bit error probability")
    plt.title("Teleportation fidelity under quantum + classical noise")
    plt.colorbar(contour, label="Average fidelity")
    plt.tight_layout()
    plt.savefig(csv_path.with_suffix(".png"), dpi=170)
    plt.close()


if __name__ == "__main__":
    result = run()
    maybe_plot(result)
    print(result)
