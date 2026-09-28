"""Elementary Schwarzschild-horizon calculations.

These helpers are valid for idealized, non-rotating, uncharged black holes and
for positions outside the event horizon.
"""

from __future__ import annotations

import math

G = 6.67430e-11
C = 299_792_458.0
M_SUN = 1.98847e30


def _require_finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def schwarzschild_radius(mass_kg: float) -> float:
    mass_kg = _require_finite("mass_kg", mass_kg)
    if mass_kg <= 0.0:
        raise ValueError("mass_kg must be positive")
    return 2.0 * G * mass_kg / C**2


def gravitational_redshift_factor(mass_kg: float, radius_m: float) -> float:
    """Return distant/static received-to-emitted frequency ratio outside the horizon."""
    radius_m = _require_finite("radius_m", radius_m)
    rs = schwarzschild_radius(mass_kg)
    if radius_m <= rs:
        raise ValueError("radius_m must be outside the Schwarzschild radius")
    # (r-rs)/r avoids cancellation in 1-rs/r for radii extremely close to rs.
    return math.sqrt((radius_m - rs) / radius_m)


def coordinate_escape_delay(mass_kg: float, r_start_m: float, r_end_m: float) -> float:
    """Exact Schwarzschild coordinate time for an outgoing radial null ray.

    The result includes the flat-space propagation term and is a coordinate-time
    interval, not a local observer's proper time or only an excess gravitational
    delay.
    """
    r_start_m = _require_finite("r_start_m", r_start_m)
    r_end_m = _require_finite("r_end_m", r_end_m)
    rs = schwarzschild_radius(mass_kg)
    if not (r_end_m > r_start_m > rs):
        raise ValueError("Require r_end_m > r_start_m > Schwarzschild radius")
    logarithmic_term = math.log(r_end_m - rs) - math.log(r_start_m - rs)
    return (r_end_m - r_start_m) / C + (rs / C) * logarithmic_term
