"""Deliberately simplified Hayden-Preskill-inspired recovery proxy.

This module is *not* a numerical implementation or quantitative prediction of
the Hayden-Preskill protocol. The threshold and sigmoid are chosen toy-model
parameters intended only for software experiments and qualitative demonstrations.
"""

from __future__ import annotations

import math


def recovery_proxy_score(
    message_qubits: int,
    collected_qubits: int,
    scrambling_strength: float = 1.0,
) -> float:
    """Return an uncalibrated sigmoid recovery *proxy* in the interval [0, 1].

    The threshold ``2 * message_qubits`` and sigmoid slope are modeling choices,
    not a result derived from the Hayden-Preskill decoding theorem.
    """
    if not isinstance(message_qubits, int) or isinstance(message_qubits, bool) or message_qubits <= 0:
        raise ValueError("message_qubits must be a positive integer")
    if (
        not isinstance(collected_qubits, int)
        or isinstance(collected_qubits, bool)
        or collected_qubits < 0
    ):
        raise ValueError("collected_qubits must be a non-negative integer")
    scrambling_strength = float(scrambling_strength)
    if not math.isfinite(scrambling_strength) or scrambling_strength <= 0.0:
        raise ValueError("scrambling_strength must be finite and positive")

    threshold = 2.0 * message_qubits
    x = scrambling_strength * (collected_qubits - threshold) / message_qubits
    if x >= 0.0:
        return 1.0 / (1.0 + math.exp(-x))
    exp_x = math.exp(x)
    return exp_x / (1.0 + exp_x)


def recovery_probability(
    message_qubits: int,
    collected_qubits: int,
    scrambling_strength: float = 1.0,
) -> float:
    """Compatibility name for :func:`recovery_proxy_score`.

    Despite the historical function name, the returned value is an arbitrary
    toy-model proxy score and must not be interpreted as a calibrated physical
    recovery probability.
    """
    return recovery_proxy_score(message_qubits, collected_qubits, scrambling_strength)
