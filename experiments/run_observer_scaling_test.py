"""Compare near-horizon communication scaling for static and infalling emitters.

Schwarzschild, geometrized G=c=M=1. For a static emitter, received/emitted
frequency squared scales as f. For a radial emitter freely falling from rest at
infinity and emitting outward, it scales as [f/(1+sqrt(1-f))]^2.

At low SNR, capacity is proportional to the squared frequency-transfer factor.
If capacity scales as epsilon**p while escape delay scales as
-(1/(2*kappa))*ln(epsilon), then

    ln(C) + 2*p*kappa*T

has a finite near-horizon limit.
"""
from __future__ import annotations
import math

KAPPA = 0.25

def metric_f(r):
    return 1.0 - 2.0/r

def tortoise(r):
    return r + 2.0*math.log(r/2.0 - 1.0)

def static_g2(f):
    return f

def infall_g2(f):
    g = f/(1.0 + math.sqrt(1.0-f))
    return g*g

def main():
    eps = [1e-3, 1e-5, 1e-7, 1e-9]
    cases = [("static", static_g2, 1.0), ("infall", infall_g2, 2.0)]
    for name, transfer, exponent in cases:
        print("\n" + name)
        print("epsilon,g2,H_p1,H_general")
        for e in eps:
            r = 2.0*(1.0+e)
            f = metric_f(r)
            g2 = transfer(f)
            T = -tortoise(r)
            h1 = math.log(g2) + 2.0*KAPPA*T
            hg = math.log(g2) + 2.0*exponent*KAPPA*T
            print(f"{e:.3e},{g2:.12e},{h1:.12e},{hg:.12e}")
    print("\nPrediction: static uses p=1; infalling outward emission uses p=2.")
    print("General asymptotic slope: d ln(C)/dT -> -2*p*kappa.")

if __name__ == "__main__":
    main()
