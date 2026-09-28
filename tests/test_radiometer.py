import math

import pytest

from horizonlink.detectors.radiometer import (
    BOLTZMANN_CONSTANT,
    integrated_radiometer_snr,
    minimum_detectable_signal_power,
    power_snr,
    snr_to_db,
    thermal_noise_power,
)


def test_thermal_noise_power_matches_k_t_b():
    expected = BOLTZMANN_CONSTANT * 290.0 * 1.0e6
    assert thermal_noise_power(290.0, 1.0e6) == pytest.approx(expected, rel=1e-12)


def test_power_snr_is_signal_over_noise_power():
    noise = thermal_noise_power(100.0, 2.0e6)
    assert power_snr(3.0 * noise, 100.0, 2.0e6) == pytest.approx(3.0)


def test_radiometer_integration_improves_as_square_root_time():
    first = integrated_radiometer_snr(1.0e-18, 50.0, 1.0e6, 1.0)
    fourth = integrated_radiometer_snr(1.0e-18, 50.0, 1.0e6, 4.0)
    assert fourth == pytest.approx(2.0 * first, rel=1e-12)


def test_minimum_detectable_signal_round_trip():
    target = 5.0
    power = minimum_detectable_signal_power(80.0, 1.0e5, 10.0, target)
    recovered = integrated_radiometer_snr(power, 80.0, 1.0e5, 10.0)
    assert recovered == pytest.approx(target, rel=1e-12)


def test_snr_to_db():
    assert snr_to_db(100.0) == pytest.approx(20.0)


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        thermal_noise_power(0.0, 1.0)
    with pytest.raises(ValueError):
        power_snr(-1.0, 10.0, 1.0)
    with pytest.raises(ValueError):
        integrated_radiometer_snr(1.0, 10.0, 1.0, 0.0)
    with pytest.raises(ValueError):
        minimum_detectable_signal_power(10.0, 1.0, 1.0, 0.0)
    with pytest.raises(ValueError):
        snr_to_db(0.0)


def test_noise_power_scales_linearly_with_bandwidth():
    narrow = thermal_noise_power(100.0, 1.0e3)
    wide = thermal_noise_power(100.0, 1.0e6)
    assert math.isclose(wide / narrow, 1000.0)
