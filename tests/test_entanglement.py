import math

import numpy as np
import pytest

from horizonlink.quantum.entanglement import (
    partial_trace_two_qubit,
    purity,
    standard_chsh_value,
    von_neumann_entropy,
)
from horizonlink.quantum.states import bell_phi_plus, density_matrix


def test_bell_state_is_globally_pure_but_locally_maximally_mixed():
    rho = density_matrix(bell_phi_plus())
    reduced = partial_trace_two_qubit(rho, keep=0)

    assert purity(rho) == pytest.approx(1.0, abs=1e-12)
    assert reduced == pytest.approx(np.eye(2) / 2.0, abs=1e-12)
    assert von_neumann_entropy(reduced) == pytest.approx(1.0, abs=1e-12)


def test_bell_state_reaches_tsirelson_bound_for_standard_settings():
    rho = density_matrix(bell_phi_plus())
    assert standard_chsh_value(rho) == pytest.approx(2.0 * math.sqrt(2.0), abs=1e-12)


def test_product_state_does_not_violate_standard_chsh_setting():
    zero_zero = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    rho = density_matrix(zero_zero)
    assert abs(standard_chsh_value(rho)) <= 2.0 + 1e-12
