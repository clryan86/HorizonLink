"""Three-qubit quantum teleportation toy model.

The circuit here is standard quantum teleportation implemented directly with
NumPy density matrices. Optional Pauli noise is applied to Bob's half of the
Bell pair before the protocol. This is a quantum-information analogue only;
it is not a model of sending information through or out of a black-hole event
horizon.
"""

from __future__ import annotations

import math

import numpy as np

from horizonlink.quantum.states import H, I2, X, Y, Z, bell_phi_plus, density_matrix


def _single_qubit_operator(gate: np.ndarray, target: int) -> np.ndarray:
    if target not in (0, 1, 2):
        raise ValueError("target must be 0, 1, or 2")
    factors = [I2, I2, I2]
    factors[target] = gate
    return np.kron(np.kron(factors[0], factors[1]), factors[2])


def _cnot(control: int, target: int) -> np.ndarray:
    if control == target or control not in (0, 1, 2) or target not in (0, 1, 2):
        raise ValueError("control and target must be distinct qubits 0, 1, or 2")

    unitary = np.zeros((8, 8), dtype=complex)
    for basis in range(8):
        bits = [(basis >> 2) & 1, (basis >> 1) & 1, basis & 1]
        out = bits.copy()
        if bits[control]:
            out[target] ^= 1
        mapped = (out[0] << 2) | (out[1] << 1) | out[2]
        unitary[mapped, basis] = 1.0
    return unitary


def _projector(m0: int, m1: int) -> np.ndarray:
    ket0 = np.array([1.0, 0.0], dtype=complex)
    ket1 = np.array([0.0, 1.0], dtype=complex)
    p0 = np.outer(ket1 if m0 else ket0, ket1 if m0 else ket0)
    p1 = np.outer(ket1 if m1 else ket0, ket1 if m1 else ket0)
    return np.kron(np.kron(p0, p1), I2)


def _reduced_bob(rho: np.ndarray) -> np.ndarray:
    """Trace out Alice's first two qubits from a three-qubit density matrix."""
    result = np.zeros((2, 2), dtype=complex)
    for q0 in (0, 1):
        for q1 in (0, 1):
            for a in (0, 1):
                for b in (0, 1):
                    i = (q0 << 2) | (q1 << 1) | a
                    j = (q0 << 2) | (q1 << 1) | b
                    result[a, b] += rho[i, j]
    return result


def _noise_on_bob(rho: np.ndarray, error_probability: float) -> np.ndarray:
    if not 0.0 <= error_probability <= 1.0:
        raise ValueError("error_probability must be between 0 and 1")
    p = error_probability
    if p == 0.0:
        return rho
    noisy = (1.0 - p) * rho
    for gate in (X, Y, Z):
        op = _single_qubit_operator(gate, 2)
        noisy += (p / 3.0) * (op @ rho @ op.conj().T)
    return noisy


def teleport(
    input_state: np.ndarray,
    *,
    resource_error_probability: float = 0.0,
) -> np.ndarray:
    """Teleport one qubit and return Bob's output density matrix.

    Qubit order is: input (q0), Alice's Bell qubit (q1), Bob's Bell qubit (q2).
    The result averages over Alice's four measurement outcomes after applying
    the corresponding classical corrections to Bob's qubit.
    """
    psi = np.asarray(input_state, dtype=complex)
    if psi.shape != (2,):
        raise ValueError("input_state must contain two amplitudes")
    norm = np.linalg.norm(psi)
    if norm == 0:
        raise ValueError("input_state cannot be zero")
    psi = psi / norm

    initial = np.kron(density_matrix(psi), density_matrix(bell_phi_plus()))
    rho = _noise_on_bob(initial, resource_error_probability)

    cnot = _cnot(0, 1)
    rho = cnot @ rho @ cnot.conj().T
    h0 = _single_qubit_operator(H, 0)
    rho = h0 @ rho @ h0.conj().T

    bob = np.zeros((2, 2), dtype=complex)
    total_probability = 0.0

    for m0 in (0, 1):
        for m1 in (0, 1):
            projector = _projector(m0, m1)
            branch = projector @ rho @ projector
            probability = float(np.real_if_close(np.trace(branch)).real)
            if probability <= 0.0:
                continue
            branch /= probability

            correction = np.eye(2, dtype=complex)
            if m1:
                correction = X @ correction
            if m0:
                correction = Z @ correction
            correction3 = _single_qubit_operator(correction, 2)
            branch = correction3 @ branch @ correction3.conj().T

            bob += probability * _reduced_bob(branch)
            total_probability += probability

    if not math.isclose(total_probability, 1.0, rel_tol=1e-10, abs_tol=1e-10):
        raise RuntimeError("teleportation measurement probabilities did not sum to one")

    return bob
