"""Map teleportation fidelity over quantum-resource and classical-channel noise.

The experiment writes a CSV grid. It is a standard quantum-information toy
model and does not represent communication through a classical event horizon.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from horizonlink.protocols.teleportation import teleport
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
    path.parent.mkdir(parents=True, exist_ok=True)

    resource_values = np.linspace(0.0, 1.0, resource_points)
    classical_values = np.linspace(0.0, 0.5, classical_points)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "resource_error_probability",
                "classical_bit_error_probability",
                "average_fidelity",
            ]
        )
        for resource_error in resource_values:
            for classical_error in classical_values:
                writer.writerow(
                    [
                        float(resource_error),
                        float(classical_error),
                        average_fidelity(float(resource_error), float(classical_error)),
                    ]
                )

    return path


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
