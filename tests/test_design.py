import pytest

from horizonlink.detectors.radiometer import integrated_radiometer_snr
from horizonlink.horizons.design import maximum_receiver_distance, required_transmitter_power
from horizonlink.horizons.link_budget import horizon_link_fraction
from horizonlink.horizons.schwarzschild import M_SUN, schwarzschild_radius


def test_required_transmitter_power_hits_target_snr():
    mass = 10.0 * M_SUN
    radius = 2.0 * schwarzschild_radius(mass)
    distance = 1.0e9
    aperture = 100.0
    temperature = 50.0
    bandwidth = 1.0e6
    integration = 10.0
    target = 5.0

    transmitter_power = required_transmitter_power(
        mass,
        radius,
        distance,
        aperture,
        temperature,
        bandwidth,
        integration,
        target,
    )
    received_power = transmitter_power * horizon_link_fraction(
        mass, radius, distance, aperture
    )
    snr = integrated_radiometer_snr(
        received_power,
        temperature,
        bandwidth,
        integration,
    )
    assert snr == pytest.approx(target, rel=1e-12)


def test_maximum_receiver_distance_hits_target_snr():
    mass = 5.0 * M_SUN
    radius = 3.0 * schwarzschild_radius(mass)
    transmitter_power = 1.0e8
    aperture = 1.0e4
    temperature = 30.0
    bandwidth = 1.0e5
    integration = 100.0
    target = 10.0

    distance = maximum_receiver_distance(
        mass,
        radius,
        transmitter_power,
        aperture,
        temperature,
        bandwidth,
        integration,
        target,
    )
    received_power = transmitter_power * horizon_link_fraction(
        mass, radius, distance, aperture
    )
    snr = integrated_radiometer_snr(
        received_power,
        temperature,
        bandwidth,
        integration,
    )
    assert snr == pytest.approx(target, rel=1e-12)


def test_longer_integration_reduces_required_transmitter_power():
    mass = M_SUN
    radius = 2.0 * schwarzschild_radius(mass)
    short = required_transmitter_power(
        mass, radius, 1.0e8, 10.0, 100.0, 1.0e6, 1.0, 5.0
    )
    long = required_transmitter_power(
        mass, radius, 1.0e8, 10.0, 100.0, 1.0e6, 100.0, 5.0
    )
    assert long == pytest.approx(short / 10.0, rel=1e-12)


def test_max_distance_rejects_impossible_target():
    mass = M_SUN
    radius = 1.0001 * schwarzschild_radius(mass)
    with pytest.raises(ValueError, match="cannot be reached"):
        maximum_receiver_distance(
            mass,
            radius,
            transmitter_power_w=1.0e-30,
            aperture_area_m2=1.0,
            system_temperature_k=300.0,
            bandwidth_hz=1.0e9,
            integration_time_s=1.0,
            target_snr=100.0,
        )
