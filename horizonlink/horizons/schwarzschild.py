"""Elementary Schwarzschild-horizon calculations.

These helpers are valid for idealized, non-rotating, uncharged black holes and
for positions outside the event horizon.
"""

from __future__ import annotations

import math

G = 6.67430e-11
C = 299_792_458.0
M_SUN = 1.98847e30


def schwarzschild_radius(mass_kg: float) -> float:
    if mass_kg <= 0:
        raise ValueError("mass_kg must be positive")
    return 2.0 * G * mass_kg / C**2


def gravitational_redshift_factor(mass_kg: float, radius_m: float) -> float:
    """Return received/emitted frequency ratio for a static emitter at r."""
    rs = schwarzschild_radius(mass_kg)
    if radius_m <= rs:
        raise ValueError("radius_m must be outside the Schwarzschild radius")
    return math.sqrt(1.0 - rs / radius_m)


def coordinate_escape_delay(mass_kg: float, r_start_m: float, r_end_m: float) -> float:
    """Approximate Schwarzschild coordinate time for an outgoing radial light ray."""
    rs = schwarzschild_radius(mass_kg)
    if not (r_end_m > r_start_m > rs):
        raise ValueError("Require r_end_m > r_start_m > Schwarzschild radius")
    return (r_end_m - r_start_m) / C + (rs / C) * math.log(
        (r_end_m - rs) / (r_start_m - rs)
    )
