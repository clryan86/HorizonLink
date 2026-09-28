"""Full Kerr ZAMO redshift stress test for the HorizonLink capacity-delay law.

For an equatorial Kerr photon with conserved E and L, define b=L/E. A ZAMO
measures

    omega_local = (E - omega(r) L) / alpha(r),

while a stationary observer at infinity measures E. Thus

    g = omega_inf / omega_local = alpha / (1 - omega b).

At low SNR with fixed emitted power/noise, C is proportional to g^2.

For generic modes with 1 - Omega_H b != 0, g^2 ~ alpha^2 ~ (r-r_+), so

    H_b = ln(C) + 2*kappa*T

remains finite as r -> r_+.

At the critical corotating boundary b = 1/Omega_H, the denominator vanishes at
the horizon. Then the scaling class changes and H_b diverges. This is the same
critical combination that appears in the Kerr horizon/superradiant bound
E - Omega_H L = 0.

This is a geometric/redshift test, not a complete wave-scattering model:
greybody factors, Teukolsky transmission, finite packets and detector response
remain separate tests.
"""
from __future__ import annotations

import argparse
import math


def horizon_data(chi: float):
    if not (0.0 < abs(chi) < 1.0):
        raise ValueError("Use 0 < |chi| < 1 for this Kerr boundary test")
    d = math.sqrt(1.0 - chi * chi)
    rp, rm = 1.0 + d, 1.0 - d
    a = chi
    kappa = (rp - rm) / (2.0 * (rp * rp + a * a))
    omega_h = a / (rp * rp + a * a)
    return rp, rm, kappa, omega_h


def equatorial_zamo(r: float, a: float, rp: float, rm: float):
    delta = (r - rp) * (r - rm)
    A = (r * r + a * a) ** 2 - a * a * delta
    alpha2 = delta * r * r / A
    omega = 2.0 * a * r / A
    return alpha2, omega


def tortoise(r: float, a: float, rp: float, rm: float) -> float:
    ap = (rp * rp + a * a) / (rp - rm)
    am = -(rm * rm + a * a) / (rp - rm)
    return r + ap * math.log(r - rp) + am * math.log(r - rm)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spins", default="0.5,0.9,0.99")
    p.add_argument("--fractions", default="0,0.5,0.9,0.99,1.0",
                   help="b/bcrit values, bcrit=1/Omega_H")
    p.add_argument("--eps", default="1e-3,1e-5,1e-7,1e-9")
    args = p.parse_args()

    spins = [float(x) for x in args.spins.split(",")]
    fracs = [float(x) for x in args.fractions.split(",")]
    epsilons = [float(x) for x in args.eps.split(",")]

    print("chi,b_over_bcrit,epsilon,kappa,Omega_H,g2,H_full")
    for chi in spins:
        rp, rm, kappa, omega_h = horizon_data(chi)
        bcrit = 1.0 / omega_h
        for frac in fracs:
            b = frac * bcrit
            for eps in epsilons:
                r = rp * (1.0 + eps)
                alpha2, omega = equatorial_zamo(r, chi, rp, rm)
                denom = 1.0 - omega * b
                g2 = alpha2 / (denom * denom)
                rstar = tortoise(r, chi, rp, rm)
                # T = const - rstar; constants only shift H.
                H = math.log(g2) - 2.0 * kappa * rstar
                print(
                    f"{chi:.9g},{frac:.9g},{eps:.3e},{kappa:.12e},"
                    f"{omega_h:.12e},{g2:.12e},{H:.12e}"
                )
            print()

    print("Expected:")
    print("  b/bcrit != 1: H_full -> finite spin- and b-dependent constant.")
    print("  b/bcrit == 1: critical horizon-frequency class; H_full diverges.")
    print("Analytic generic-mode shift relative to b=0:")
    print("  Delta H -> -2 ln|1 - Omega_H b|.")
    print("Critical condition: E - Omega_H L = 0.")


if __name__ == "__main__":
    main()
