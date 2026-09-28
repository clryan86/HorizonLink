import math

import pytest

from horizonlink.detectors.radiometer import (
    BOLTZMANN_CONSTANT,
    integrated_radiometer_snr,
    minimum_detectable_signal_power,
    power_snr,
    required_integration_time,
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


def test_required_integration_time_round_trip():
    signal_power = 3.0e-18
    temperature = 70.0
    bandwidth = 2.0e5
    target = 8.0
    integration_time = required_integration_time(
        signal_power,
        temperature,
        bandwidth,
        target,
    )
    recovered = integrated_radiometer_snr(
        signal_power,
        temperature,
        bandwidth,
        integration_time,
    )
    assert recovered == pytest.approx(target, rel=1e-12)


def test_required_integration_time_rejects_zero_signal():
    with pytest.raises(ValueError, match="positive"):
        required_integration_time(0.0, 50.0, 1.0e6, 5.0)


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


def test_nonfinite_inputs_are_rejected():
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            thermal_noise_power(bad, 1.0)
        with pytest.raises(ValueError):
            thermal_noise_power(10.0, bad)
        with pytest.raises(ValueError):
            power_snr(bad, 10.0, 1.0)
        with pytest.raises(ValueError):
            integrated_radiometer_snr(1.0, 10.0, 1.0, bad)
        with pytest.raises(ValueError):
            minimum_detectable_signal_power(10.0, 1.0, 1.0, bad)
        with pytest.raises(ValueError):
            required_integration_time(1.0, 10.0, 1.0, bad)


def test_bandwidth_times_integration_overflow_is_rejected():
    with pytest.raises(OverflowError, match=r"bandwidth \* integration_time_s"):
        integrated_radiometer_snr(1.0, 10.0, 1.0e308, 1.0e308)


def test_noise_power_scales_linearly_with_bandwidth():
    narrow = thermal_noise_power(100.0, 1.0e3)
    wide = thermal_noise_power(100.0, 1.0e6)
    assert math.isclose(wide / narrow, 1000.0)
