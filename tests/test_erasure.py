import numpy as np
import pytest

from horizonlink.channels.erasure import capacity, transmit


def test_capacity_limits():
    assert capacity(0.0) == 1.0
    assert capacity(1.0) == 0.0


def test_transmit_all_or_none():
    bits = np.array([0, 1, 1, 0])
    assert np.array_equal(transmit(bits, 0.0, rng=1), bits)
    assert np.all(transmit(bits, 1.0, rng=1) == -1)


def test_invalid_probability():
    with pytest.raises(ValueError):
        capacity(1.1)
