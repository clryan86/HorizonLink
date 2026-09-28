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

_DENSITY_ATOL = 1.0e-10


def normalize(state: np.ndarray) -> np.ndarray:
    """Return a numerically stable normalized one-dimensional state vector."""
    state = np.asarray(state, dtype=complex)
    if state.ndim != 1 or state.size == 0:
        raise ValueError("state must be a nonempty one-dimensional vector")
    if not np.all(np.isfinite(state.real)) or not np.all(np.isfinite(state.imag)):
        raise ValueError("state amplitudes must be finite")

    scale = float(np.max(np.abs(state)))
    if scale == 0.0:
        raise ValueError("state cannot be the zero vector")

    scaled = state / scale
    norm = np.linalg.norm(scaled)
    if not np.isfinite(norm) or norm == 0.0:
        raise ValueError("state norm is not finite and nonzero")
    return scaled / norm


def validate_density_matrix(
    rho: np.ndarray,
    *,
    dimension: int | None = None,
    atol: float = _DENSITY_ATOL,
) -> np.ndarray:
    """Validate and return a finite Hermitian positive-semidefinite density matrix.

    Tiny negative eigenvalues within ``atol`` are tolerated as floating-point
    roundoff, but material violations are rejected rather than silently clipped.
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1] or rho.shape[0] == 0:
        raise ValueError("rho must be a nonempty square matrix")
    if dimension is not None and rho.shape != (dimension, dimension):
        raise ValueError(f"rho must have shape ({dimension}, {dimension})")
    if not np.all(np.isfinite(rho.real)) or not np.all(np.isfinite(rho.imag)):
        raise ValueError("rho entries must be finite")
    if not np.allclose(rho, rho.conj().T, atol=atol, rtol=0.0):
        raise ValueError("rho must be Hermitian")

    trace = np.trace(rho)
    if abs(trace.imag) > atol or not math.isclose(float(trace.real), 1.0, abs_tol=atol, rel_tol=0.0):
        raise ValueError("rho must have real trace one")

    eigenvalues = np.linalg.eigvalsh(rho)
    if float(np.min(eigenvalues)) < -atol:
        raise ValueError("rho must be positive semidefinite")
    return rho


def qubit_state(theta: float, phi: float = 0.0) -> np.ndarray:
    """Return cos(theta/2)|0> + exp(i phi) sin(theta/2)|1>."""
    if not math.isfinite(theta) or not math.isfinite(phi):
        raise ValueError("theta and phi must be finite")
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
    """Fidelity between a pure target state and a valid density matrix."""
    psi = normalize(target_state)
    rho = validate_density_matrix(rho, dimension=psi.size)
    value = np.vdot(psi, rho @ psi)
    if abs(value.imag) > _DENSITY_ATOL:
        raise ValueError("fidelity acquired a material imaginary component")
    result = float(value.real)
    if result < -_DENSITY_ATOL or result > 1.0 + _DENSITY_ATOL:
        raise ValueError("fidelity lies outside the physical interval [0, 1]")
    return min(1.0, max(0.0, result))


def pauli_depolarize(rho: np.ndarray, error_probability: float) -> np.ndarray:
    """Apply the single-qubit Pauli depolarizing channel.

    Convention: with probability 1-p no error occurs; with total probability p,
    X, Y, or Z is applied uniformly. Complete depolarization occurs at p=3/4;
    p=1 is a uniform non-identity Pauli error channel, not the maximally mixed
    channel. For a pure state, the average state fidelity is 1 - 2p/3.
    """
    if not math.isfinite(error_probability) or not 0.0 <= error_probability <= 1.0:
        raise ValueError("error_probability must be finite and between 0 and 1")
    rho = validate_density_matrix(rho, dimension=2)
    p = error_probability
    result = (1.0 - p) * rho + (p / 3.0) * sum(
        gate @ rho @ gate.conj().T for gate in (X, Y, Z)
    )
    return validate_density_matrix(result, dimension=2)
