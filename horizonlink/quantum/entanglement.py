"""Entanglement and mixed-state diagnostics for two-qubit toy models."""

from __future__ import annotations

import math

import numpy as np

from horizonlink.quantum.states import X, Z, validate_density_matrix


def purity(rho: np.ndarray) -> float:
    """Return Tr(rho^2), equal to one for a pure density matrix."""
    rho = validate_density_matrix(rho)
    value = np.trace(rho @ rho)
    if abs(value.imag) > 1.0e-10:
        raise ValueError("purity acquired a material imaginary component")
    result = float(value.real)
    if result < -1.0e-10 or result > 1.0 + 1.0e-10:
        raise ValueError("purity lies outside the physical interval [0, 1]")
    return min(1.0, max(0.0, result))


def von_neumann_entropy(rho: np.ndarray, base: float = 2.0) -> float:
    """Return -Tr(rho log rho), defaulting to bits."""
    rho = validate_density_matrix(rho)
    if not math.isfinite(base) or base <= 0.0 or math.isclose(base, 1.0, abs_tol=0.0):
        raise ValueError("base must be finite, positive, and different from one")

    eigenvalues = np.linalg.eigvalsh(rho).real
    eigenvalues = np.where(eigenvalues < 0.0, 0.0, eigenvalues)
    nonzero = eigenvalues[eigenvalues > 1.0e-15]
    if nonzero.size == 0:
        return 0.0
    return float(-np.sum(nonzero * np.log(nonzero)) / math.log(base))


def partial_trace_two_qubit(rho: np.ndarray, keep: int) -> np.ndarray:
    """Trace out one qubit from a valid two-qubit density matrix.

    ``keep=0`` returns the first qubit; ``keep=1`` returns the second.
    """
    rho = validate_density_matrix(rho, dimension=4)
    if keep not in (0, 1):
        raise ValueError("keep must be 0 or 1")

    tensor = rho.reshape(2, 2, 2, 2)
    if keep == 0:
        reduced = np.trace(tensor, axis1=1, axis2=3)
    else:
        reduced = np.trace(tensor, axis1=0, axis2=2)
    return validate_density_matrix(reduced, dimension=2)


def standard_chsh_value(rho: np.ndarray) -> float:
    """Return CHSH expectation for one fixed setting optimal for |Phi+>.

    A0=Z, A1=X, B0=(Z+X)/sqrt(2), B1=(Z-X)/sqrt(2).
    Local-hidden-variable models satisfy |S| <= 2, while |Phi+> reaches
    the Tsirelson bound 2*sqrt(2) for these settings. Failure to violate this
    one fixed CHSH setting does not by itself prove that a state is separable.
    """
    rho = validate_density_matrix(rho, dimension=4)
    b0 = (Z + X) / math.sqrt(2.0)
    b1 = (Z - X) / math.sqrt(2.0)
    operator = np.kron(Z, b0) + np.kron(Z, b1) + np.kron(X, b0) - np.kron(X, b1)
    value = np.trace(rho @ operator)
    if abs(value.imag) > 1.0e-10:
        raise ValueError("CHSH expectation acquired a material imaginary component")
    result = float(value.real)
    bound = 2.0 * math.sqrt(2.0)
    if abs(result) > bound + 1.0e-9:
        raise ValueError("CHSH expectation exceeds the quantum Tsirelson bound")
    return result
