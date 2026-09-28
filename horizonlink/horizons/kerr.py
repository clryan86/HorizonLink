"""Elementary Kerr black-hole exterior calculations.

The spin parameter used here is the dimensionless Kerr spin
``chi = c J / (G M^2)`` with ``|chi| <= 1``. Radii are Boyer-Lindquist radial
coordinates expressed in metres.
"""

from __future__ import annotations

import math

from horizonlink.horizons.schwarzschild import C, G


def gravitational_radius(mass_kg: float) -> float:
    """Return GM/c^2 in metres."""
    if mass_kg <= 0.0:
        raise ValueError("mass_kg must be positive")
    return G * mass_kg / C**2


def _validate_spin(chi: float) -> float:
    if not -1.0 <= chi <= 1.0:
        raise ValueError("dimensionless Kerr spin chi must satisfy |chi| <= 1")
    return float(chi)


def horizon_radii(mass_kg: float, chi: float) -> tuple[float, float]:
    """Return the outer and inner Kerr horizon radii ``(r_plus, r_minus)``."""
    rg = gravitational_radius(mass_kg)
    chi = _validate_spin(chi)
    root = math.sqrt(max(0.0, 1.0 - chi**2))
    return rg * (1.0 + root), rg * (1.0 - root)


def outer_horizon_radius(mass_kg: float, chi: float) -> float:
    """Return the outer event-horizon radius in metres."""
    return horizon_radii(mass_kg, chi)[0]


def inner_horizon_radius(mass_kg: float, chi: float) -> float:
    """Return the inner (Cauchy) horizon radius in metres."""
    return horizon_radii(mass_kg, chi)[1]


def static_limit_radius(mass_kg: float, chi: float, polar_angle_rad: float) -> float:
    """Return the outer static-limit radius at Boyer-Lindquist polar angle theta.

    The region between this surface and the outer horizon is the ergoregion.
    At the poles the static limit touches the event horizon; at the equator it
    is located at 2 GM/c^2 for every allowed spin magnitude.
    """
    rg = gravitational_radius(mass_kg)
    chi = _validate_spin(chi)
    cos_theta = math.cos(polar_angle_rad)
    root = math.sqrt(max(0.0, 1.0 - chi**2 * cos_theta**2))
    return rg * (1.0 + root)


def horizon_angular_velocity(mass_kg: float, chi: float) -> float:
    """Return Kerr horizon angular velocity in radians per second.

    Positive and negative spin values preserve their rotation sign.
    """
    _validate_spin(chi)
    r_plus = outer_horizon_radius(mass_kg, chi)
    return C * chi / (2.0 * r_plus)


def frame_dragging_angular_velocity(
    mass_kg: float,
    chi: float,
    radius_m: float,
    polar_angle_rad: float = math.pi / 2.0,
) -> float:
    """Return the ZAMO frame-dragging angular velocity in rad/s.

    This is ``-g_tphi/g_phiphi`` for the Kerr metric in Boyer-Lindquist
    coordinates. The function is defined here at and outside the outer horizon.
    At ``r = r_+`` it reduces to the horizon angular velocity.
    """
    rg = gravitational_radius(mass_kg)
    chi = _validate_spin(chi)
    r_plus = outer_horizon_radius(mass_kg, chi)
    if radius_m < r_plus:
        raise ValueError("radius_m must be at or outside the outer Kerr horizon")

    a = chi * rg
    sin_theta = math.sin(polar_angle_rad)
    delta = radius_m**2 - 2.0 * rg * radius_m + a**2
    big_a = (radius_m**2 + a**2) ** 2 - a**2 * delta * sin_theta**2
    if big_a <= 0.0:
        raise ValueError("Kerr metric denominator is non-positive at this coordinate")

    return C * (2.0 * rg * a * radius_m) / big_a
