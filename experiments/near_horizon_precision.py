"""Audit numerical precision in Schwarzschild near-horizon echo timing.

This experiment deliberately compares two representations of the same surface:

1. naive float64 radius: r = rs * (1 + epsilon)
2. offset representation: epsilon is retained directly

The second avoids losing epsilon when 1 + epsilon rounds to 1.  Decimal is used
as an independent high-precision reference.  This is a numerical-conditioning
experiment, not evidence for physical gravitational-wave echoes.
"""

from __future__ import annotations

import argparse
import csv
import math
from decimal import Decimal, localcontext
from pathlib import Path

C = 299_792_458.0
G = 6.67430e-11
M_SUN = 1.98847e30


def schwarzschild_radius(mass_solar: float) -> float:
    return 2.0 * G * mass_solar * M_SUN / C**2


def photon_sphere_tortoise_over_rs() -> float:
    # r_ph = 1.5 rs; r*/rs = 1.5 + ln(0.5)
    return 1.5 + math.log(0.5)


def echo_delay_offset(mass_solar: float, epsilon: float) -> float:
    """Stable float64 formula that never forms 1 + epsilon."""
    rs = schwarzschild_radius(mass_solar)
    surface_over_rs = 1.0 + epsilon + math.log(epsilon)
    return 2.0 * rs * (photon_sphere_tortoise_over_rs() - surface_over_rs) / C


def echo_delay_naive(mass_solar: float, epsilon: float) -> float:
    """Naive radius calculation; returns inf when the surface collapses to rs."""
    rs = schwarzschild_radius(mass_solar)
    r = rs * (1.0 + epsilon)
    x = r / rs - 1.0
    if x <= 0.0:
        return math.inf
    rstar_surface = r + rs * math.log(x)
    r_ph = 1.5 * rs
    rstar_ph = r_ph + rs * math.log(r_ph / rs - 1.0)
    return 2.0 * (rstar_ph - rstar_surface) / C


def echo_delay_decimal(mass_solar: float, epsilon_text: str, precision: int = 100) -> Decimal:
    """Independent arbitrary-precision reference, returned in seconds."""
    with localcontext() as ctx:
        ctx.prec = precision
        d2 = Decimal(2)
        d15 = Decimal('1.5')
        mass = Decimal(str(mass_solar))
        eps = Decimal(epsilon_text)
        g = Decimal('6.67430e-11')
        c = Decimal('299792458')
        msun = Decimal('1.98847e30')
        rs = d2 * g * mass * msun / (c * c)
        ph = d15 + Decimal('0.5').ln()
        surface = Decimal(1) + eps + eps.ln()
        return d2 * rs * (ph - surface) / c


def sweep(mass_solar: float, min_exp: int, max_exp: int):
    rows = []
    first_collapse = None
    worst_finite = None
    for exponent in range(min_exp, max_exp - 1, -1):
        eps_text = f"1e{exponent}"
        eps = float(eps_text)
        stable = echo_delay_offset(mass_solar, eps)
        naive = echo_delay_naive(mass_solar, eps)
        reference = float(echo_delay_decimal(mass_solar, eps_text))
        stable_rel = abs(stable - reference) / abs(reference)
        if math.isfinite(naive):
            naive_rel = abs(naive - reference) / abs(reference)
            if worst_finite is None or naive_rel > worst_finite[1]:
                worst_finite = (exponent, naive_rel)
        else:
            naive_rel = math.inf
            if first_collapse is None:
                first_collapse = exponent
        rows.append((exponent, eps, naive, stable, reference, naive_rel, stable_rel))
    return rows, first_collapse, worst_finite


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mass", type=float, default=30.0, help="black-hole mass in solar masses")
    parser.add_argument("--min-exp", type=int, default=-1)
    parser.add_argument("--max-exp", type=int, default=-100)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()

    rows, first_collapse, worst_finite = sweep(args.mass, args.min_exp, args.max_exp)
    print(f"mass = {args.mass:g} M_sun")
    print(f"machine epsilon = {math.ulp(1.0):.17g}")
    print(f"first 10^n surface collapsed onto horizon in naive float64: n={first_collapse}")
    if worst_finite:
        print(f"worst finite naive relative error: 10^{worst_finite[0]} -> {worst_finite[1]:.6g}")
    print("\n exponent       naive_s        stable_s       reference_s     naive_relerr    stable_relerr")
    for row in rows:
        exponent, _, naive, stable, reference, naive_rel, stable_rel = row
        if exponent >= -14 or exponent <= -18 or exponent in (-15, -16, -17):
            print(f"{exponent:8d} {naive:14.7g} {stable:14.7g} {reference:14.7g} {naive_rel:14.7g} {stable_rel:14.7g}")

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["exponent", "epsilon", "naive_s", "stable_s", "reference_s", "naive_relerr", "stable_relerr"])
            writer.writerows(rows)
        print(f"wrote {args.csv}")


if __name__ == "__main__":
    main()
