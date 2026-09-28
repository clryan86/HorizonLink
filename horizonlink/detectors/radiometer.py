"""Simple thermal-noise and radiometer sensitivity helpers.

These functions are intentionally transparent approximations. They are useful for
comparing received signal power against an idealized thermal-noise floor, but they
do not replace a full receiver model with gain, efficiency, sky temperature,
atmosphere, polarization, quantization, interference, or calibration effects.
"""

from __future__ import annotations

import math

BOLTZMANN_CONSTANT = 1.380649e-23  # J/K, exact SI value


def _positive(value: float, name: str) -> float:
    value = float(value)
    if value <= 0.0:
        raise ValueError(f"{name} must be positive")
    return value


def thermal_noise_power(system_temperature_k: float, bandwidth_hz: float) -> float:
    """Return ideal Rayleigh-Jeans thermal-noise power ``k T B`` in watts."""
    temperature = _positive(system_temperature_k, "system_temperature_k")
    bandwidth = _positive(bandwidth_hz, "bandwidth_hz")
    return BOLTZMANN_CONSTANT * temperature * bandwidth


def power_snr(
    signal_power_w: float,
    system_temperature_k: float,
    bandwidth_hz: float,
) -> float:
    """Return instantaneous signal-power / thermal-noise-power ratio."""
    signal_power = float(signal_power_w)
    if signal_power < 0.0:
        raise ValueError("signal_power_w cannot be negative")
    return signal_power / thermal_noise_power(system_temperature_k, bandwidth_hz)


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
    return power_snr(signal_power_w, system_temperature_k, bandwidth) * math.sqrt(
        bandwidth * integration_time
    )


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
    noise_power = thermal_noise_power(system_temperature_k, bandwidth)
    return target * noise_power / math.sqrt(bandwidth * integration_time)


def snr_to_db(snr_linear: float) -> float:
    """Convert a positive linear power SNR to decibels."""
    snr = _positive(snr_linear, "snr_linear")
    return 10.0 * math.log10(snr)
