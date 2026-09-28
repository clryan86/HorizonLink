import math

import numpy as np
import pytest

from horizonlink.channels.binary_symmetric import capacity_bits_per_use, transmit as bsc_transmit
from horizonlink.channels.erasure import transmit as erasure_transmit
from horizonlink.horizons.kerr import horizon_radii, static_limit_radius
from horizonlink.horizons.link_budget import geometric_collection_fraction
from horizonlink.horizons.schwarzschild import M_SUN, gravitational_redshift_factor, schwarzschild_radius
from horizonlink.protocols.hayden_preskill import recovery_proxy_score
from horizonlink.search.grid import maximize


def test_channel_input_is_validated_before_integer_casting():
    with pytest.raises(ValueError):
        bsc_transmit([0.2, 1.8], 0.1, seed=1)
    with pytest.raises(ValueError):
        erasure_transmit([0.2, 1.8], 0.1, rng=1)
    with pytest.raises(ValueError):
        bsc_transmit(np.array([256, 257]), 0.1, seed=1)


def test_bsc_capacity_supports_full_probability_interval():
    assert capacity_bits_per_use(1.0) == pytest.approx(1.0)
    assert capacity_bits_per_use(0.9) == pytest.approx(capacity_bits_per_use(0.1))


def test_nonfinite_link_and_kerr_inputs_are_rejected():
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            geometric_collection_fraction(bad, 1.0)
        with pytest.raises(ValueError):
            geometric_collection_fraction(1000.0, bad)
        with pytest.raises(ValueError):
            static_limit_radius(M_SUN, 0.8, bad)


def test_grid_search_rejects_nan_objective():
    with pytest.raises(ValueError, match="non-finite"):
        maximize(lambda x: float("nan") if x == 0 else 10.0, {"x": [0, 1]})


def test_recovery_proxy_uses_overflow_safe_sigmoid():
    low = recovery_proxy_score(8, 0, 1000.0)
    high = recovery_proxy_score(8, 1000, 1000.0)
    assert 0.0 <= low < 1.0e-100
    assert high == pytest.approx(1.0)


def test_near_horizon_redshift_uses_stable_expression():
    rs = schwarzschild_radius(M_SUN)
    radius = np.nextafter(rs, math.inf)
    value = gravitational_redshift_factor(M_SUN, radius)
    expected = math.sqrt((radius - rs) / radius)
    assert value == pytest.approx(expected, rel=1.0e-15)


def test_tiny_spin_inner_kerr_root_does_not_cancel_to_zero():
    _, r_minus = horizon_radii(M_SUN, 1.0e-9)
    assert r_minus > 0.0
