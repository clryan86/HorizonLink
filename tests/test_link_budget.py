import pytest

from horizonlink.horizons.link_budget import (
    geometric_collection_fraction,
    horizon_link_fraction,
    redshift_power_factor,
    redshifted_frequency,
)
from horizonlink.horizons.schwarzschild import M_SUN, schwarzschild_radius


def test_redshift_weakens_near_horizon_signal():
    mass = 10.0 * M_SUN
    rs = schwarzschild_radius(mass)
    near = redshift_power_factor(mass, 1.01 * rs)
    far = redshift_power_factor(mass, 10.0 * rs)
    assert 0.0 < near < far < 1.0


def test_frequency_is_redshifted():
    mass = 5.0 * M_SUN
    rs = schwarzschild_radius(mass)
    emitted = 1.0e9
    received = redshifted_frequency(mass, 2.0 * rs, emitted)
    assert 0.0 < received < emitted


def test_collection_fraction_scales_with_area():
    small = geometric_collection_fraction(1000.0, 1.0)
    large = geometric_collection_fraction(1000.0, 10.0)
    assert large == pytest.approx(10.0 * small)


def test_link_fraction_rejects_inside_horizon():
    mass = M_SUN
    rs = schwarzschild_radius(mass)
    with pytest.raises(ValueError):
        horizon_link_fraction(mass, rs, 1.0e6, 1.0)
