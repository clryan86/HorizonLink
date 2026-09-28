import numpy as np
import pytest

from horizonlink.channels.binary_symmetric import (
    binary_entropy,
    capacity_bits_per_use,
    transmit,
)


def test_capacity_endpoints():
    assert capacity_bits_per_use(0.0) == pytest.approx(1.0)
    assert capacity_bits_per_use(0.5) == pytest.approx(0.0)


def test_binary_entropy_is_symmetric():
    assert binary_entropy(0.2) == pytest.approx(binary_entropy(0.8))


def test_transmit_is_reproducible():
    bits = np.array([0, 1, 0, 1, 1, 0], dtype=np.int8)
    first = transmit(bits, 0.25, seed=42)
    second = transmit(bits, 0.25, seed=42)
    assert np.array_equal(first, second)


def test_invalid_capacity_probability():
    with pytest.raises(ValueError):
        capacity_bits_per_use(0.6)
