"""Simple thermal-noise and radiometer sensitivity helpers.

These functions are intentionally transparent approximations. They are useful for
comparing received signal power against an idealized thermal-noise floor, but they
do not replace a full receiver model with gain, efficiency, sky temperature,
atmosphere, polarization, quantization, interference, or calibration effects.
"""

from __future__ import annotations

import math
import sys

BOLTZMANN_CONSTANT = 1.380649e-23  # J/K, exact SI value


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _positive(value: float, name: str) -> float:
    value = _finite(value, name)
    if value <= 0.0:
        raise ValueError(f"{name} must be positive")
    return value


def _nonnegative(value: float, name: str) -> float:
    value = _finite(value, name)
    if value < 0.0:
        raise ValueError(f"{name} cannot be negative")
    return value


def thermal_noise_power(system_temperature_k: float, bandwidth_hz: float) -> float:
    """Return ideal Rayleigh-Jeans thermal-noise power ``k T B`` in watts."""
    temperature = _positive(system_temperature_k, "system_temperature_k")
    bandwidth = _positive(bandwidth_hz, "bandwidth_hz")
    value = BOLTZMANN_CONSTANT * temperature * bandwidth
    if not math.isfinite(value):
        raise OverflowError("thermal-noise power overflowed")
    return value


def power_snr(
    signal_power_w: float,
    system_temperature_k: float,
    bandwidth_hz: float,
) -> float:
    """Return instantaneous signal-power / thermal-noise-power ratio."""
    signal_power = _nonnegative(signal_power_w, "signal_power_w")
    value = signal_power / thermal_noise_power(system_temperature_k, bandwidth_hz)
    if not math.isfinite(value):
        raise OverflowError("power SNR overflowed")
    return value


def integrated_radiometer_snr(
    signal_power_w: float,
    system_temperature_k: float,
    bandwidth_hz: float,
    integration_time_s: float,
) -> float:
    """Return an idealized total-power radiometer SNR after integration.

    The approximation multiplies the instantaneous power ratio by
    ``sqrt(B * tau)``, corresponding to averaging independent thermal-noise
    samples over bandwidth ``B`` and integration time ``tau``. Real receivers
    can differ by order-unity factors and by systematic-noise floors.
    """
    bandwidth = _positive(bandwidth_hz, "bandwidth_hz")
    integration_time = _positive(integration_time_s, "integration_time_s")
    sample_count = bandwidth * integration_time
    if not math.isfinite(sample_count):
        raise OverflowError("bandwidth * integration_time_s overflowed")
    value = power_snr(signal_power_w, system_temperature_k, bandwidth) * math.sqrt(
        sample_count
    )
    if not math.isfinite(value):
        raise OverflowError("integrated radiometer SNR overflowed")
    return value


def minimum_detectable_signal_power(
    system_temperature_k: float,
    bandwidth_hz: float,
    integration_time_s: float,
    target_snr: float = 5.0,
) -> float:
    """Return signal power needed to reach ``target_snr`` in the idealized model."""
    target = _positive(target_snr, "target_snr")
    bandwidth = _positive(bandwidth_hz, "bandwidth_hz")
    integration_time = _positive(integration_time_s, "integration_time_s")
    sample_count = bandwidth * integration_time
    if not math.isfinite(sample_count):
        raise OverflowError("bandwidth * integration_time_s overflowed")
    noise_power = thermal_noise_power(system_temperature_k, bandwidth)
    value = target * noise_power / math.sqrt(sample_count)
    if not math.isfinite(value):
        raise OverflowError("minimum detectable signal power overflowed")
    return value


def required_integration_time(
    signal_power_w: float,
    system_temperature_k: float,
    bandwidth_hz: float,
    target_snr: float = 5.0,
) -> float:
    """Return integration time needed to reach ``target_snr`` in seconds.

    This is the analytic inverse of :func:`integrated_radiometer_snr` under the
    same ideal white-noise assumptions. A zero signal can never reach a
    positive target SNR and is rejected.
    """
    target = _positive(target_snr, "target_snr")
    bandwidth = _positive(bandwidth_hz, "bandwidth_hz")
    instantaneous = power_snr(signal_power_w, system_temperature_k, bandwidth)
    if instantaneous <= 0.0:
        raise ValueError("signal_power_w must be positive to solve integration time")

    log_time = 2.0 * (math.log(target) - math.log(instantaneous)) - math.log(bandwidth)
    if log_time > math.log(sys.float_info.max):
        raise OverflowError("required integration time overflowed")
    value = math.exp(log_time)
    if value == 0.0 or not math.isfinite(value):
        raise OverflowError("required integration time is outside floating-point range")
    return value


def snr_to_db(snr_linear: float) -> float:
    """Convert a positive linear power SNR to decibels."""
    snr = _positive(snr_linear, "snr_linear")
    return 10.0 * math.log10(snr)
