import pytest

from horizonlink.horizons.schwarzschild import M_SUN, gravitational_redshift_factor, schwarzschild_radius


def test_solar_schwarzschild_radius_is_about_2953_m():
    assert schwarzschild_radius(M_SUN) == pytest.approx(2953.34, rel=1e-3)


def test_redshift_factor_outside_horizon():
    rs = schwarzschild_radius(M_SUN)
    factor = gravitational_redshift_factor(M_SUN, 2.0 * rs)
    assert factor == pytest.approx(2 ** -0.5)


def test_redshift_rejects_inside_horizon():
    rs = schwarzschild_radius(M_SUN)
    with pytest.raises(ValueError):
        gravitational_redshift_factor(M_SUN, rs)
