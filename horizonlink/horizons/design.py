"""Inverse-design helpers for the simplified exterior communication model.

These functions answer practical questions such as "what transmitter power is
needed for a target integrated SNR?" while staying inside HorizonLink's existing
Schwarzschild + geometric-collection + ideal radiometer assumptions.
"""

from __future__ import annotations

import math

from horizonlink.detectors.radiometer import minimum_detectable_signal_power
from horizonlink.horizons.link_budget import horizon_link_fraction, redshift_power_factor


def _positive_finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def required_transmitter_power(
    mass_kg: float,
    emitter_radius_m: float,
    receiver_distance_m: float,
    aperture_area_m2: float,
    system_temperature_k: float,
    bandwidth_hz: float,
    integration_time_s: float,
    target_snr: float = 5.0,
) -> float:
    """Return transmitter power needed to reach a target integrated SNR."""
    received_required = minimum_detectable_signal_power(
        system_temperature_k,
        bandwidth_hz,
        integration_time_s,
        target_snr,
    )
    fraction = horizon_link_fraction(
        mass_kg,
        emitter_radius_m,
        receiver_distance_m,
        aperture_area_m2,
    )
    if not math.isfinite(fraction) or fraction <= 0.0:
        raise ValueError("link fraction is zero or non-finite; target SNR is unreachable")
    value = received_required / fraction
    if not math.isfinite(value):
        raise OverflowError("required transmitter power overflowed")
    return value


def maximum_receiver_distance(
    mass_kg: float,
    emitter_radius_m: float,
    transmitter_power_w: float,
    aperture_area_m2: float,
    system_temperature_k: float,
    bandwidth_hz: float,
    integration_time_s: float,
    target_snr: float = 5.0,
) -> float:
    """Return maximum receiver distance for a target integrated SNR.

    The solution assumes the uncapped isotropic geometric fraction
    ``A/(4*pi*d^2)`` at the limiting distance. If the target cannot be met even
    when all redshifted transmitter power is collected, a ``ValueError`` is
    raised.
    """
    transmitter_power = _positive_finite(transmitter_power_w, "transmitter_power_w")
    aperture_area = _positive_finite(aperture_area_m2, "aperture_area_m2")

    required_received = minimum_detectable_signal_power(
        system_temperature_k,
        bandwidth_hz,
        integration_time_s,
        target_snr,
    )
    redshift_factor = redshift_power_factor(mass_kg, emitter_radius_m)
    if not math.isfinite(redshift_factor) or redshift_factor <= 0.0:
        raise ValueError("redshift power factor is zero or non-finite")

    maximum_received = transmitter_power * redshift_factor
    if not math.isfinite(maximum_received):
        raise OverflowError("maximum received power overflowed")
    if required_received > maximum_received:
        raise ValueError(
            "target SNR cannot be reached even with unit geometric collection fraction"
        )

    # Rearrange d = sqrt(P_tx * f_redshift * A / (4*pi*P_required)).
    # Compute through logarithms when direct multiplication would overflow.
    log_distance_squared = (
        math.log(transmitter_power)
        + math.log(redshift_factor)
        + math.log(aperture_area)
        - math.log(4.0 * math.pi)
        - math.log(required_received)
    )
    log_distance = 0.5 * log_distance_squared
    if log_distance > math.log(float.fromhex("0x1.fffffffffffffp+1023")):
        raise OverflowError("maximum receiver distance overflowed")
    value = math.exp(log_distance)
    if not math.isfinite(value) or value <= 0.0:
        raise OverflowError("maximum receiver distance is non-finite")
    return value
