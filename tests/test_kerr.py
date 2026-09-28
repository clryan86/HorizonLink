import math

import pytest

from horizonlink.horizons.kerr import (
    gravitational_radius,
    horizon_angular_velocity,
    horizon_radii,
    static_limit_radius,
)
from horizonlink.horizons.schwarzschild import C, M_SUN, schwarzschild_radius


def test_zero_spin_matches_schwarzschild_outer_horizon():
    r_plus, r_minus = horizon_radii(M_SUN, 0.0)
    assert r_plus == pytest.approx(schwarzschild_radius(M_SUN), rel=1e-12)
    assert r_minus == pytest.approx(0.0, abs=1e-12)


def test_extremal_kerr_horizons_coincide_at_gravitational_radius():
    rg = gravitational_radius(M_SUN)
    r_plus, r_minus = horizon_radii(M_SUN, 1.0)
    assert r_plus == pytest.approx(rg, rel=1e-12)
    assert r_minus == pytest.approx(rg, rel=1e-12)


def test_static_limit_touches_horizon_at_pole():
    chi = 0.8
    r_plus, _ = horizon_radii(M_SUN, chi)
    assert static_limit_radius(M_SUN, chi, 0.0) == pytest.approx(r_plus, rel=1e-12)


def test_equatorial_static_limit_is_two_gravitational_radii():
    rg = gravitational_radius(M_SUN)
    value = static_limit_radius(M_SUN, 0.93, math.pi / 2.0)
    assert value == pytest.approx(2.0 * rg, rel=1e-12)


def test_horizon_angular_velocity_zero_for_nonrotating_case():
    assert horizon_angular_velocity(M_SUN, 0.0) == pytest.approx(0.0, abs=1e-12)


def test_extremal_horizon_angular_velocity():
    rg = gravitational_radius(M_SUN)
    expected = C / (2.0 * rg)
    assert horizon_angular_velocity(M_SUN, 1.0) == pytest.approx(expected, rel=1e-12)


def test_invalid_super_extremal_spin_is_rejected():
    with pytest.raises(ValueError):
        horizon_radii(M_SUN, 1.0001)
