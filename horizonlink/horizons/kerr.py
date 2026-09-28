"""Elementary Kerr black-hole exterior calculations.

The spin parameter used here is the dimensionless Kerr spin
``chi = c J / (G M^2)`` with ``|chi| <= 1``. Radii are Boyer-Lindquist radial
coordinates expressed in metres.
"""

from __future__ import annotations

import math

from horizonlink.horizons.schwarzschild import C, G


def _require_finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def gravitational_radius(mass_kg: float) -> float:
    """Return GM/c^2 in metres."""
    mass_kg = _require_finite("mass_kg", mass_kg)
    if mass_kg <= 0.0:
        raise ValueError("mass_kg must be positive")
    return G * mass_kg / C**2


def _validate_spin(chi: float) -> float:
    chi = _require_finite("chi", chi)
    if not -1.0 <= chi <= 1.0:
        raise ValueError("dimensionless Kerr spin chi must satisfy |chi| <= 1")
    return chi


def _kerr_root(chi: float) -> float:
    """Stably evaluate sqrt(1-chi^2) on the physical Kerr interval."""
    magnitude = abs(chi)
    return math.sqrt((1.0 - magnitude) * (1.0 + magnitude))


def horizon_radii(mass_kg: float, chi: float) -> tuple[float, float]:
    """Return the outer and algebraic inner Kerr roots ``(r_plus, r_minus)``.

    At ``chi=0`` the inner algebraic root is zero; it should not be interpreted
    as a regular Schwarzschild inner Cauchy horizon.
    """
    rg = gravitational_radius(mass_kg)
    chi = _validate_spin(chi)
    root = _kerr_root(chi)
    r_plus = rg * (1.0 + root)
    # Rationalized form avoids catastrophic cancellation for very small spin.
    r_minus = rg * (chi * chi) / (1.0 + root)
    return r_plus, r_minus


def outer_horizon_radius(mass_kg: float, chi: float) -> float:
    """Return the outer event-horizon radius in metres."""
    return horizon_radii(mass_kg, chi)[0]


def inner_horizon_radius(mass_kg: float, chi: float) -> float:
    """Return the algebraic inner Kerr root in metres."""
    return horizon_radii(mass_kg, chi)[1]


def static_limit_radius(mass_kg: float, chi: float, polar_angle_rad: float) -> float:
    """Return the outer static-limit radius at Boyer-Lindquist polar angle theta.

    The region between this surface and the outer horizon is the ergoregion.
    At the poles the static limit touches the event horizon; at the equator it
    is located at 2 GM/c^2 for every allowed spin magnitude.
    """
    rg = gravitational_radius(mass_kg)
    chi = _validate_spin(chi)
    polar_angle_rad = _require_finite("polar_angle_rad", polar_angle_rad)
    product = abs(chi * math.cos(polar_angle_rad))
    root = math.sqrt((1.0 - product) * (1.0 + product))
    return rg * (1.0 + root)


def horizon_angular_velocity(mass_kg: float, chi: float) -> float:
    """Return Kerr horizon angular velocity in radians per second.

    Positive and negative spin values preserve their rotation sign.
    """
    chi = _validate_spin(chi)
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
    coordinates. The value at ``r=r_+`` is the limiting horizon angular
    velocity; it does not represent a timelike observer remaining on the
    horizon.
    """
    rg = gravitational_radius(mass_kg)
    chi = _validate_spin(chi)
    radius_m = _require_finite("radius_m", radius_m)
    polar_angle_rad = _require_finite("polar_angle_rad", polar_angle_rad)
    r_plus = outer_horizon_radius(mass_kg, chi)
    if radius_m < r_plus:
        raise ValueError("radius_m must be at or outside the outer Kerr horizon")

    # Dimensionless form avoids fourth-power overflow in metre-valued radii.
    x = radius_m / rg
    if not math.isfinite(x):
        raise ValueError("radius_m / gravitational_radius exceeds supported float range")
    sin_theta = math.sin(polar_angle_rad)
    chi2 = chi * chi
    delta_bar = x * x - 2.0 * x + chi2
    denominator = (x * x + chi2) ** 2 - chi2 * delta_bar * sin_theta**2
    if not math.isfinite(denominator) or denominator <= 0.0:
        raise ValueError("Kerr metric denominator is non-positive or non-finite")

    dimensionless = (2.0 * chi * x) / denominator
    return (C / rg) * dimensionless
