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


def test_classical_side_channel_errors_reduce_fidelity():
    state = qubit_state(0.0)
    clean = teleport(state)
    noisy = teleport(state, classical_bit_error_probability=0.25)

    assert fidelity_pure(state, clean) == pytest.approx(1.0, abs=1e-12)
    assert fidelity_pure(state, noisy) < 1.0
    assert np.trace(noisy) == pytest.approx(1.0)


def test_fully_randomized_classical_bits_destroy_correction_information():
    state = qubit_state(np.pi / 2.0, 0.37)
    output = teleport(state, classical_bit_error_probability=0.5)
    assert fidelity_pure(state, output) == pytest.approx(0.5, abs=1e-12)


def test_resource_noise_probability_is_validated():
    with pytest.raises(ValueError):
        teleport(qubit_state(0.0), resource_error_probability=1.01)


def test_classical_noise_probability_is_validated():
    with pytest.raises(ValueError):
        teleport(qubit_state(0.0), classical_bit_error_probability=-0.01)
