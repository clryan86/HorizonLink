"""Numerically derive the Schwarzschild scalar greybody exponent and feed it
into HorizonLink's capacity-delay prediction.

We solve the massless scalar Regge-Wheeler equation (G=c=M=1)

    d^2 psi/dr_*^2 + [omega^2 - V_l(r)] psi = 0
    V_l = f(r)[l(l+1)/r^2 + 2/r^3],   f=1-2/r.

Boundary condition: unit-amplitude ingoing wave at the future horizon.
At large r we decompose

    psi = A_in exp(-i omega r_*) + A_out exp(+i omega r_*),

so the transmission/greybody probability is Gamma_l = 1/|A_in|^2.

At low frequency, the solver should recover Gamma_l ~ omega^beta with
beta -> 2l+2.

For a static near-horizon transmitter with fixed LOCAL carrier frequency,
omega_infinity ~ sqrt(x), x=r-r_h. The gravitational signal-power factor is
~x. Multiplying by Gamma_l(omega_infinity) gives

    received low-SNR capacity C ~ x^(1 + beta/2),

so HorizonLink predicts p = 1 + beta/2 and therefore

    d ln C / dT -> -2 p kappa.

If beta -> 2l+2, this becomes the sharp mode prediction

    p -> l+2,
    d ln C/dT -> -2(l+2) kappa.

This experiment derives beta numerically from the wave equation rather than
putting p in by hand.
"""
from __future__ import annotations

import argparse
import cmath
import math


def f(r: float) -> float:
    return 1.0 - 2.0 / r


def potential(r: float, ell: int) -> float:
    fr = f(r)
    return fr * (ell * (ell + 1.0) / (r * r) + 2.0 / (r ** 3))


def tortoise(r: float) -> float:
    return r + 2.0 * math.log(r / 2.0 - 1.0)


def deriv(r: float, psi: complex, y: complex, omega: float, ell: int):
    fr = f(r)
    return y / fr, -(omega * omega - potential(r, ell)) * psi / fr


def rk4(r: float, psi: complex, y: complex, h: float, omega: float, ell: int):
    k1p, k1y = deriv(r, psi, y, omega, ell)
    k2p, k2y = deriv(
        r + 0.5*h, psi + 0.5*h*k1p, y + 0.5*h*k1y, omega, ell
    )
    k3p, k3y = deriv(
        r + 0.5*h, psi + 0.5*h*k2p, y + 0.5*h*k2y, omega, ell
    )
    k4p, k4y = deriv(r + h, psi + h*k3p, y + h*k3y, omega, ell)
    return (
        psi + h*(k1p + 2*k2p + 2*k3p + k4p)/6.0,
        y + h*(k1y + 2*k2y + 2*k3y + k4y)/6.0,
    )


def greybody(omega: float, ell: int, rmax: float | None = None) -> float:
    r = 2.0 * (1.0 + 1.0e-5)
    if rmax is None:
        rmax = max(300.0, 30.0 / omega)

    rs = tortoise(r)
    psi = cmath.exp(-1j * omega * rs)
    y = -1j * omega * psi  # d psi / d r_*

    while r < rmax:
        # Keep r-steps small close to the coordinate singularity.
        h = min(0.02, max(1.0e-6, 0.1*(r-2.0)), rmax-r)
        psi, y = rk4(r, psi, y, h, omega, ell)
        r += h

    rs = tortoise(r)
    em = cmath.exp(-1j * omega * rs)
    # psi=Ain*em+Aout*ep and y=-iw*Ain*em+iw*Aout*ep
    ain = (psi - y/(1j*omega)) / (2.0*em)
    return 1.0 / (abs(ain)**2)


def linear_slope(xs, ys) -> float:
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    xm = sum(lx)/len(lx)
    ym = sum(ly)/len(ly)
    num = sum((x-xm)*(y-ym) for x, y in zip(lx, ly))
    den = sum((x-xm)**2 for x in lx)
    return num/den


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ells", default="0,1,2")
    ap.add_argument("--omegas", default="0.03,0.04,0.05,0.07")
    args = ap.parse_args()

    ells = [int(v) for v in args.ells.split(",")]
    omegas = [float(v) for v in args.omegas.split(",")]
    kappa = 0.25  # Schwarzschild M=1

    print("ell,omega,Gamma")
    for ell in ells:
        gammas = []
        for omega in omegas:
            g = greybody(omega, ell)
            gammas.append(g)
            print(f"{ell},{omega:.12e},{g:.12e}")

        beta = linear_slope(omegas, gammas)
        p = 1.0 + 0.5*beta
        predicted_latency_slope = -2.0*p*kappa
        print(
            f"# ell={ell} beta_fit={beta:.12g} beta_expected={2*ell+2} "
            f"p_fit={p:.12g} p_expected={ell+2} "
            f"dlnC_dT_pred={predicted_latency_slope:.12g}"
        )
        print()

    print("Low-frequency target: beta -> 2l+2.")
    print("Derived channel target: p -> l+2.")
    print("Therefore d ln C/dT -> -2(l+2)kappa for a static fixed-local-frequency source.")


if __name__ == "__main__":
    main()
