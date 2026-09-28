"""Kerr falsification test for the HorizonLink near-horizon capacity-delay law.

Hypothesis (geometrized G=c=M=1): for a subextremal Kerr horizon, an exterior
low-SNR channel whose received power is proportional to the local ZAMO lapse
alpha^2 has a finite near-horizon combination

    H = ln(C) + 2*kappa*T,

because alpha^2 ~ (r-r_+) while the outgoing Boyer-Lindquist delay has
T ~ -(1/(2*kappa))*ln(r-r_+).

This script isolates the singular near-horizon geometry. It is NOT a complete
Kerr communication model: greybody factors, angular mode coupling,
superradiance, finite wave packets, detector motion and full Teukolsky
propagation remain future falsification tests.
"""
from __future__ import annotations
import argparse, math


def horizon_data(chi: float):
    if not (0.0 <= abs(chi) < 1.0):
        raise ValueError("Require subextremal |chi|<1")
    d = math.sqrt(1.0-chi*chi)
    rp, rm = 1.0+d, 1.0-d
    a = chi
    kappa = (rp-rm)/(2.0*(rp*rp+a*a))
    omega_h = a/(rp*rp+a*a)
    return rp, rm, kappa, omega_h


def zamo_lapse2(r: float, a: float, rp: float, rm: float) -> float:
    # Equatorial Kerr: alpha^2 = Delta*rho^2/A, rho^2=r^2.
    delta=(r-rp)*(r-rm)
    A=(r*r+a*a)**2-a*a*delta
    return delta*r*r/A


def tortoise(r: float, a: float, rp: float, rm: float) -> float:
    # Additive constant irrelevant. dr*/dr=(r^2+a^2)/Delta.
    ap=(rp*rp+a*a)/(rp-rm)
    am=-(rm*rm+a*a)/(rp-rm)
    return r + ap*math.log(r-rp) + am*math.log(r-rm)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--spins", default="0,.5,.9,.99,.999")
    p.add_argument("--eps", default="1e-3,1e-5,1e-7,1e-9")
    args=p.parse_args()
    spins=[float(x) for x in args.spins.split(',')]
    epsilons=[float(x) for x in args.eps.split(',')]
    print("chi,epsilon,kappa,omega_h,alpha2,H_geometry")
    for chi in spins:
        rp,rm,kappa,omega_h=horizon_data(chi)
        for eps in epsilons:
            r=rp*(1.0+eps)
            alpha2=zamo_lapse2(r,chi,rp,rm)
            rstar=tortoise(r,chi,rp,rm)
            # For an outgoing ray to a fixed receiver, T = const-rstar.
            # Receiver/additive constants shift H but cannot affect convergence.
            H=math.log(alpha2)-2.0*kappa*rstar
            print(f"{chi:.9g},{eps:.3e},{kappa:.12e},{omega_h:.12e},{alpha2:.12e},{H:.12e}")
        print()
    print("PASS criterion: H_geometry converges to a finite spin-dependent constant as epsilon->0 for every |chi|<1.")
    print("CAUTION: chi->1 and epsilon->0 do not commute; exact extremality is a distinct scaling class.")

if __name__ == '__main__':
    main()
