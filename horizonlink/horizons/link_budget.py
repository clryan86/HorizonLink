"""Toy link-budget helpers near an idealized Schwarzschild horizon.

These functions do not model communication from inside a classical event
horizon. They estimate how gravitational redshift and geometric spreading can
reduce a signal emitted from a static location outside the horizon.
"""

from __future__ import annotations

import math

from .schwarzschild import gravitational_redshift_factor, schwarzschild_radius


def redshifted_frequency(mass_kg: float, radius_m: float, emitted_hz: float) -> float:
    """Return the frequency measured by a distant observer."""
    if emitted_hz <= 0:
        raise ValueError("emitted_hz must be positive")
    return emitted_hz * gravitational_redshift_factor(mass_kg, radius_m)


def redshift_power_factor(mass_kg: float, radius_m: float) -> float:
    """Return a simple distant-observer power attenuation factor.

    In this toy model, photon energy and emission rate each acquire one factor
    of sqrt(1-rs/r), giving a total factor of (1-rs/r).
    """
    factor = gravitational_redshift_factor(mass_kg, radius_m)
    return factor * factor


def geometric_collection_fraction(distance_m: float, aperture_area_m2: float = 1.0) -> float:
    """Fraction of isotropic power intercepted by a collecting area.

    This intentionally avoids folding antenna wavelength/gain assumptions into
    the horizon model. The fraction is A/(4*pi*d^2), capped at one.
    """
    if distance_m <= 0 or aperture_area_m2 <= 0:
        raise ValueError("distance_m and aperture_area_m2 must be positive")
    return min(1.0, aperture_area_m2 / (4.0 * math.pi * distance_m**2))


def horizon_link_fraction(
    mass_kg: float,
    emitter_radius_m: float,
    receiver_distance_m: float,
    aperture_area_m2: float = 1.0,
) -> float:
    """Combine gravitational redshift loss with geometric collection."""
    rs = schwarzschild_radius(mass_kg)
    if emitter_radius_m <= rs:
        raise ValueError("emitter must remain outside the event horizon")
    return redshift_power_factor(mass_kg, emitter_radius_m) * geometric_collection_fraction(
        receiver_distance_m, aperture_area_m2
    )
