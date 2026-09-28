"""Minimal state-vector and density-matrix utilities.

This module intentionally stays small and transparent. It is not intended to
replace a full quantum SDK; it exists so HorizonLink's toy models can be read
and audited without hiding the math behind a large dependency stack.
"""

from __future__ import annotations

import math

import numpy as np

ZERO = np.array([1.0, 0.0], dtype=complex)
ONE = np.array([0.0, 1.0], dtype=complex)
H = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / math.sqrt(2.0)
X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def normalize(state: np.ndarray) -> np.ndarray:
    state = np.asarray(state, dtype=complex)
    norm = np.linalg.norm(state)
    if norm == 0:
        raise ValueError("state cannot be the zero vector")
    return state / norm


def qubit_state(theta: float, phi: float = 0.0) -> np.ndarray:
    """Return cos(theta/2)|0> + exp(i phi) sin(theta/2)|1>."""
    return np.array(
        [
            math.cos(theta / 2.0),
            np.exp(1.0j * phi) * math.sin(theta / 2.0),
        ],
        dtype=complex,
    )


def density_matrix(state: np.ndarray) -> np.ndarray:
    state = normalize(state)
    return np.outer(state, state.conj())


def bell_phi_plus() -> np.ndarray:
    """Return (|00> + |11>) / sqrt(2)."""
    return np.array([1.0, 0.0, 0.0, 1.0], dtype=complex) / math.sqrt(2.0)


def fidelity_pure(target_state: np.ndarray, rho: np.ndarray) -> float:
    """Fidelity between a pure target state and a density matrix."""
    psi = normalize(target_state)
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (psi.size, psi.size):
        raise ValueError("rho shape does not match target state dimension")
    value = np.vdot(psi, rho @ psi)
    return float(np.real_if_close(value).real)


def pauli_depolarize(rho: np.ndarray, error_probability: float) -> np.ndarray:
    """Apply the single-qubit Pauli depolarizing channel.

    Convention: with probability 1-p no error occurs; with total probability p,
    X, Y, or Z is applied uniformly. For a pure state, the average state
    fidelity of this channel is 1 - 2p/3.
    """
    if not 0.0 <= error_probability <= 1.0:
        raise ValueError("error_probability must be between 0 and 1")
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (2, 2):
        raise ValueError("pauli_depolarize expects a single-qubit density matrix")
    p = error_probability
    return (1.0 - p) * rho + (p / 3.0) * sum(
        gate @ rho @ gate.conj().T for gate in (X, Y, Z)
    )
