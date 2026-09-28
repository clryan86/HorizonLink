"""Simplified distant-receiver link-budget helpers near a Schwarzschild horizon.

These functions do not model communication from inside a classical event
horizon. They combine a receiver-at-infinity gravitational redshift convention
with an independently specified Euclidean geometric collection distance. The
model intentionally omits photon capture/escape cones, lensing, aperture
orientation, plasma, orbital motion, and finite-receiver gravitational shift.
"""

from __future__ import annotations

import math

from .schwarzschild import gravitational_redshift_factor, schwarzschild_radius


def _positive_finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def redshifted_frequency(mass_kg: float, radius_m: float, emitted_hz: float) -> float:
    """Return frequency measured by an idealized static receiver at infinity."""
    emitted_hz = _positive_finite("emitted_hz", emitted_hz)
    return emitted_hz * gravitational_redshift_factor(mass_kg, radius_m)


def redshift_power_factor(mass_kg: float, radius_m: float) -> float:
    """Return a simple distant-observer power attenuation factor.

    Emitted power is interpreted per unit proper time of the static emitter.
    Photon energy and arrival rate each acquire one factor of
    ``sqrt(1-rs/r)``, giving a total factor ``1-rs/r``.
    """
    factor = gravitational_redshift_factor(mass_kg, radius_m)
    return factor * factor


def geometric_collection_fraction(distance_m: float, aperture_area_m2: float = 1.0) -> float:
    """Fraction of isotropic power intercepted by a collecting area.

    ``distance_m`` is an independent Euclidean spreading distance used only in
    this toy geometric term. It is not a Boyer-Lindquist/Schwarzschild receiver
    radius. The expression is ``A/(4*pi*d^2)``, capped at one.
    """
    distance_m = _positive_finite("distance_m", distance_m)
    aperture_area_m2 = _positive_finite("aperture_area_m2", aperture_area_m2)

    # Evaluate in log space to avoid d**2 overflow and tiny-distance underflow.
    log_fraction = (
        math.log(aperture_area_m2)
        - math.log(4.0 * math.pi)
        - 2.0 * math.log(distance_m)
    )
    if log_fraction >= 0.0:
        return 1.0
    return math.exp(log_fraction)


def horizon_link_fraction(
    mass_kg: float,
    emitter_radius_m: float,
    receiver_distance_m: float,
    aperture_area_m2: float = 1.0,
) -> float:
    """Combine distant-observer redshift loss with toy geometric collection."""
    emitter_radius_m = _positive_finite("emitter_radius_m", emitter_radius_m)
    rs = schwarzschild_radius(mass_kg)
    if emitter_radius_m <= rs:
        raise ValueError("emitter must remain outside the event horizon")
    return redshift_power_factor(mass_kg, emitter_radius_m) * geometric_collection_fraction(
        receiver_distance_m, aperture_area_m2
    )
