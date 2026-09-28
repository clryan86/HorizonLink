"""Inverse-design helpers for the simplified exterior communication model.

These functions answer practical questions such as "what transmitter power is
needed for a target integrated SNR?" while staying inside HorizonLink's existing
Schwarzschild + geometric-collection + ideal radiometer assumptions.
"""

from __future__ import annotations

import math
import sys

from horizonlink.detectors.radiometer import minimum_detectable_signal_power
from horizonlink.horizons.link_budget import horizon_link_fraction, redshift_power_factor

_LOG_FLOAT_MAX = math.log(sys.float_info.max)


def _positive_finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _exp_checked(log_value: float, name: str) -> float:
    if not math.isfinite(log_value):
        raise OverflowError(f"{name} is non-finite")
    if log_value > _LOG_FLOAT_MAX:
        raise OverflowError(f"{name} overflowed")
    value = math.exp(log_value)
    if value == 0.0 or not math.isfinite(value):
        raise OverflowError(f"{name} is outside floating-point range")
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
    return _exp_checked(
        math.log(received_required) - math.log(fraction),
        "required transmitter power",
    )


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

    log_distance = 0.5 * (
        math.log(transmitter_power)
        + math.log(redshift_factor)
        + math.log(aperture_area)
        - math.log(4.0 * math.pi)
        - math.log(required_received)
    )
    return _exp_checked(log_distance, "maximum receiver distance")


def required_collecting_area(
    mass_kg: float,
    emitter_radius_m: float,
    transmitter_power_w: float,
    receiver_distance_m: float,
    system_temperature_k: float,
    bandwidth_hz: float,
    integration_time_s: float,
    target_snr: float = 5.0,
) -> float:
    """Return collecting area needed to reach a target integrated SNR.

    The inversion uses HorizonLink's isotropic geometric fraction
    ``A/(4*pi*d^2)``. If the target would require a collection fraction greater
    than one, it is impossible under this model and ``ValueError`` is raised.
    """
    transmitter_power = _positive_finite(transmitter_power_w, "transmitter_power_w")
    distance = _positive_finite(receiver_distance_m, "receiver_distance_m")
    required_received = minimum_detectable_signal_power(
        system_temperature_k,
        bandwidth_hz,
        integration_time_s,
        target_snr,
    )
    redshift_factor = redshift_power_factor(mass_kg, emitter_radius_m)
    if not math.isfinite(redshift_factor) or redshift_factor <= 0.0:
        raise ValueError("redshift power factor is zero or non-finite")

    log_required_fraction = (
        math.log(required_received)
        - math.log(transmitter_power)
        - math.log(redshift_factor)
    )
    if log_required_fraction > 0.0:
        raise ValueError(
            "target SNR cannot be reached even with unit geometric collection fraction"
        )

    log_area = log_required_fraction + math.log(4.0 * math.pi) + 2.0 * math.log(distance)
    return _exp_checked(log_area, "required collecting area")
