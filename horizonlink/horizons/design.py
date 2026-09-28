"""Inverse-design helpers for the simplified exterior communication model.

These functions answer practical questions such as "what transmitter power is
needed for a target integrated SNR?" while staying inside HorizonLink's existing
Schwarzschild + geometric-collection + ideal radiometer assumptions.
"""

from __future__ import annotations

import math

from horizonlink.detectors.radiometer import minimum_detectable_signal_power
from horizonlink.horizons.link_budget import horizon_link_fraction, redshift_power_factor


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
    return received_required / fraction


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
    transmitter_power = float(transmitter_power_w)
    aperture_area = float(aperture_area_m2)
    if transmitter_power <= 0.0:
        raise ValueError("transmitter_power_w must be positive")
    if aperture_area <= 0.0:
        raise ValueError("aperture_area_m2 must be positive")

    required_received = minimum_detectable_signal_power(
        system_temperature_k,
        bandwidth_hz,
        integration_time_s,
        target_snr,
    )
    redshift_factor = redshift_power_factor(mass_kg, emitter_radius_m)
    maximum_received = transmitter_power * redshift_factor
    if required_received > maximum_received:
        raise ValueError(
            "target SNR cannot be reached even with unit geometric collection fraction"
        )

    numerator = transmitter_power * redshift_factor * aperture_area
    return math.sqrt(numerator / (4.0 * math.pi * required_received))
