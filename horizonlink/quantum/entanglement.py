"""Entanglement and mixed-state diagnostics for two-qubit toy models."""

from __future__ import annotations

import math

import numpy as np

from horizonlink.quantum.states import X, Z


def _validate_density_matrix(rho: np.ndarray, dimension: int) -> np.ndarray:
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (dimension, dimension):
        raise ValueError(f"rho must have shape ({dimension}, {dimension})")
    if not np.allclose(rho, rho.conj().T, atol=1e-10):
        raise ValueError("rho must be Hermitian")
    trace = np.trace(rho)
    if not np.isclose(trace, 1.0, atol=1e-10):
        raise ValueError("rho must have trace one")
    return rho


def purity(rho: np.ndarray) -> float:
    """Return Tr(rho^2), equal to one for a pure state."""
    rho = np.asarray(rho, dtype=complex)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("rho must be a square matrix")
    value = np.trace(rho @ rho)
    return float(np.real_if_close(value).real)


def von_neumann_entropy(rho: np.ndarray, base: float = 2.0) -> float:
    """Return -Tr(rho log rho), defaulting to bits."""
    rho = np.asarray(rho, dtype=complex)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("rho must be a square matrix")
    if base <= 0.0 or math.isclose(base, 1.0):
        raise ValueError("base must be positive and different from one")

    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = np.clip(eigenvalues.real, 0.0, 1.0)
    nonzero = eigenvalues[eigenvalues > 1e-15]
    if nonzero.size == 0:
        return 0.0
    return float(-np.sum(nonzero * np.log(nonzero)) / math.log(base))


def partial_trace_two_qubit(rho: np.ndarray, keep: int) -> np.ndarray:
    """Trace out one qubit from a two-qubit density matrix.

    ``keep=0`` returns the first qubit; ``keep=1`` returns the second.
    """
    rho = _validate_density_matrix(rho, 4)
    if keep not in (0, 1):
        raise ValueError("keep must be 0 or 1")

    tensor = rho.reshape(2, 2, 2, 2)
    if keep == 0:
        return np.trace(tensor, axis1=1, axis2=3)
    return np.trace(tensor, axis1=0, axis2=2)


def standard_chsh_value(rho: np.ndarray) -> float:
    """Return the CHSH expectation for settings optimal for |Phi+>.

    A0=Z, A1=X, B0=(Z+X)/sqrt(2), B1=(Z-X)/sqrt(2).
    Local-hidden-variable models satisfy |S| <= 2, while |Phi+> reaches
    the Tsirelson bound 2*sqrt(2) for these settings.
    """
    rho = _validate_density_matrix(rho, 4)
    b0 = (Z + X) / math.sqrt(2.0)
    b1 = (Z - X) / math.sqrt(2.0)
    operator = np.kron(Z, b0) + np.kron(Z, b1) + np.kron(X, b0) - np.kron(X, b1)
    value = np.trace(rho @ operator)
    return float(np.real_if_close(value).real)
