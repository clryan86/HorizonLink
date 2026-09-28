import numpy as np
import pytest

from horizonlink.protocols.teleportation import teleport
from horizonlink.quantum.states import fidelity_pure, qubit_state


@pytest.mark.parametrize(
    ("theta", "phi"),
    [
        (0.0, 0.0),
        (np.pi, 0.0),
        (np.pi / 2.0, 0.0),
        (np.pi / 2.0, np.pi),
        (np.pi / 2.0, np.pi / 2.0),
        (1.17, 0.73),
    ],
)
def test_ideal_teleportation_preserves_qubit(theta, phi):
    state = qubit_state(theta, phi)
    output = teleport(state)
    assert fidelity_pure(state, output) == pytest.approx(1.0, abs=1e-12)
    assert np.trace(output) == pytest.approx(1.0)


def test_resource_depolarization_reduces_fidelity_predictably():
    state = qubit_state(0.0)
    output = teleport(state, resource_error_probability=0.3)
    assert fidelity_pure(state, output) == pytest.approx(0.8, abs=1e-12)


def test_resource_noise_probability_is_validated():
    with pytest.raises(ValueError):
        teleport(qubit_state(0.0), resource_error_probability=1.01)
