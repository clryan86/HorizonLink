import numpy as np
import pytest

from horizonlink.quantum.entanglement import purity, standard_chsh_value, von_neumann_entropy
from horizonlink.quantum.states import density_matrix, fidelity_pure, normalize, pauli_depolarize


def test_normalize_handles_extreme_amplitude_scales():
    large = normalize(np.array([1.0e300, 1.0e300], dtype=complex))
    small = normalize(np.array([1.0e-300, 1.0e-300], dtype=complex))
    expected = np.array([2.0**-0.5, 2.0**-0.5])
    assert large == pytest.approx(expected)
    assert small == pytest.approx(expected)


def test_normalize_rejects_nonvector_and_nonfinite_input():
    with pytest.raises(ValueError):
        normalize(np.eye(2))
    with pytest.raises(ValueError):
        normalize(np.array([1.0, np.nan]))


def test_invalid_density_operator_is_rejected_by_all_diagnostics():
    invalid = np.diag([2.0, -1.0]).astype(complex)
    with pytest.raises(ValueError):
        purity(invalid)
    with pytest.raises(ValueError):
        von_neumann_entropy(invalid)
    with pytest.raises(ValueError):
        fidelity_pure(np.array([1.0, 0.0]), invalid)
    with pytest.raises(ValueError):
        pauli_depolarize(invalid, 0.2)


def test_nonhermitian_density_operator_is_rejected():
    invalid = np.array([[0.5, 1.0], [0.0, 0.5]], dtype=complex)
    with pytest.raises(ValueError):
        von_neumann_entropy(invalid)


def test_unphysical_two_qubit_operator_cannot_fake_chsh_violation():
    phi_plus = np.array([1.0, 0.0, 0.0, 1.0], dtype=complex) / np.sqrt(2.0)
    psi_minus = np.array([0.0, 1.0, -1.0, 0.0], dtype=complex) / np.sqrt(2.0)
    invalid = 2.0 * density_matrix(phi_plus) - density_matrix(psi_minus)
    with pytest.raises(ValueError):
        standard_chsh_value(invalid)


def test_complete_pauli_depolarization_occurs_at_three_quarters():
    rho = density_matrix(np.array([1.0, 0.0]))
    output = pauli_depolarize(rho, 0.75)
    assert output == pytest.approx(np.eye(2) / 2.0, abs=1.0e-12)
