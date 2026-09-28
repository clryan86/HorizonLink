import math

from experiments.near_horizon_precision import (
    echo_delay_decimal,
    echo_delay_naive,
    echo_delay_offset,
)


def test_offset_matches_decimal_reference():
    for exponent in (-8, -12, -16, -30, -100):
        text = f"1e{exponent}"
        reference = float(echo_delay_decimal(30.0, text))
        value = echo_delay_offset(30.0, float(text))
        assert math.isclose(value, reference, rel_tol=2e-15, abs_tol=0.0)


def test_naive_radius_eventually_collapses_to_horizon():
    assert math.isinf(echo_delay_naive(30.0, 1e-16))
    assert math.isfinite(echo_delay_offset(30.0, 1e-16))


def test_echo_delay_scales_linearly_with_mass():
    d1 = echo_delay_offset(1.0, 1e-20)
    d30 = echo_delay_offset(30.0, 1e-20)
    assert math.isclose(d30 / d1, 30.0, rel_tol=2e-15)
