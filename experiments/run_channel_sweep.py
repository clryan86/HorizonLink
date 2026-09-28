"""Run a first reproducible HorizonLink parameter sweep."""

from __future__ import annotations

from horizonlink.channels.erasure import capacity
from horizonlink.protocols.hayden_preskill import recovery_probability
from horizonlink.search.grid import maximize


def score(erasure_probability: float, collected_qubits: int) -> float:
    recoverability = recovery_probability(
        message_qubits=8,
        collected_qubits=collected_qubits,
        scrambling_strength=1.2,
    )
    return capacity(erasure_probability) * recoverability


def main() -> None:
    params, value = maximize(
        score,
        {
            "erasure_probability": [0.0, 0.1, 0.25, 0.5, 0.75],
            "collected_qubits": [4, 8, 12, 16, 20, 24, 32],
        },
    )
    print("HorizonLink first sweep")
    print(f"best parameters: {params}")
    print(f"combined recoverability score: {value:.6f}")


if __name__ == "__main__":
    main()
