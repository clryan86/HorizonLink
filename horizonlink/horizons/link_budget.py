"""Toy optical/radio link-budget helpers near an idealized horizon.

These functions do not model communication from inside a classical event
horizon. They estimate how redshift and geometric spreading can reduce a
signal emitted from a static location outside a Schwarzschild horizon.
"""

from __future__ import annotations

import math

from .schwarzschild import gravitational_redshift_factor, schwarzschild_radius


def redshifted_frequency(mass_kg: float, radius_m: float, emitted_hz: float) -> float:
    if emitted_hz <= 0:
        raise ValueError("emitted_hz must be positive")
    return emitted_hz * gravitational_redshift_factor(mass_kg, radius_m)


def redshift_power_factor(mass_kg: float, radius_m: float) -> float:
    """Return a simple energy-rate attenuation factor for a distant observer.

    In this toy model, photon energy and emission rate each acquire one factor
    of sqrt(1-rs/r), yielding a total factor of (1-rs/r).
    """
    factor = gravitational_redshift_factor(mass_kg, radius_m)
    return factor * factor


def free_space_power_fraction(distance_m: float, wavelength_m: float, aperture_gain: float = 1.0) -> float:
    """Approximate isotropic free-space received/transmitted power fraction.

    The result is capped at 1.0 because this is a simplified far-field model,
    not a near-field antenna calculation.
    """
    if distance_m <= 0 or wavelength_m <= 0 or aperture_gain <= 0:
        raise ValueError("distance_m, wavelength_m and aperture_gain must be positive")
    fraction = aperture_gain * (wavelength_m / (4.0 * math.pi * distance_m)) ** 2
    return min(1.0, fraction)


def horizon_link_fraction(
    mass_kg: float,
    emitter_radius_m: float,
    receiver_distance_m: float,
    emitted_hz: float,
    aperture_gain: float = 1.0,
) -> float:
    """Combine gravitational redshift loss with free-space spreading."""
    rs = schwarzschild_radius(mass_kg)
    if emitter_radius_m <= rs:
        raise ValueError("emitter must remain outside the event horizon")
    if emitted_hz <= 0:
        raise ValueError("emitted_hz must be positive")
    c = 299_792_458.0
    wavelength = c / redshifted_frequency(mass_kg, emitter_radius_m, emitted_hz)
    return redshift_power_factor(mass_kg, emitter_radius_m) * free_space_power_fraction(
        receiver_distance_m, wavelength, aperture_gain
    )
