"""A deliberately simplified Hayden-Preskill-inspired recovery toy model.

This is not a full quantum-gravity calculation. It provides a tunable proxy for
how recovery probability might improve once the collected radiation subsystem
exceeds an information-size threshold.
"""

from __future__ import annotations

import math


def recovery_probability(message_qubits: int, collected_qubits: int, scrambling_strength: float = 1.0) -> float:
    if message_qubits <= 0:
        raise ValueError("message_qubits must be positive")
    if collected_qubits < 0:
        raise ValueError("collected_qubits cannot be negative")
    if scrambling_strength <= 0:
        raise ValueError("scrambling_strength must be positive")

    threshold = 2.0 * message_qubits
    x = scrambling_strength * (collected_qubits - threshold) / max(message_qubits, 1)
    return 1.0 / (1.0 + math.exp(-x))
