import math

import pytest

from horizonlink.channels.gaussian import (
    capacity_from_snr,
    capacity_from_snr_db,
    snr_db_to_linear,
)


def test_small_snr_capacity_uses_stable_log1p():
    value = capacity_from_snr(1.0e-20, 1.0e6)
    expected = 1.0e6 * math.log1p(1.0e-20) / math.log(2.0)
    assert value == pytest.approx(expected, rel=1.0e-12)
    assert value > 0.0


def test_db_capacity_remains_finite_for_huge_snr():
    value = capacity_from_snr_db(4000.0, 1.0)
    assert math.isfinite(value)
    assert value > 1000.0


def test_db_to_linear_rejects_unrepresentable_range():
    with pytest.raises(OverflowError):
        snr_db_to_linear(4000.0)


def test_nonfinite_inputs_are_rejected():
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            capacity_from_snr(bad, 1.0)
        with pytest.raises(ValueError):
            snr_db_to_linear(bad)
