"""Stress-test HorizonLink against transmitter protocol dependence.

The previous mode law p=l+2 assumes a STATIC transmitter holding LOCAL carrier
frequency fixed as it approaches a Schwarzschild horizon. That operational
choice matters.

This script compares three asymptotic protocols analytically:

A) fixed local frequency: omega_inf ~ x^(1/2).  Redshift power ~ x and scalar
   greybody Gamma_l ~ omega_inf^(2l+2) ~ x^(l+1), giving p=l+2.

B) fixed asymptotic frequency: local transmitter frequency must grow as
   x^(-1/2). Gamma_l is then constant with x (for fixed omega_inf), while the
   gravitational power factor contributes x, giving p=1.

C) fixed local frequency but idealized no exterior barrier: p=1.

For any p in a non-extremal horizon class,
    d ln C/dT -> -2 p kappa.

The point is falsification/qualification: l+2 is NOT universal across source
protocols. The more general exponent law survives, while the discrete l+2
sequence belongs to a clearly specified operational protocol.
"""
from __future__ import annotations
import argparse


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ells',default='0,1,2,3')
    ap.add_argument('--kappa',type=float,default=0.25)
    args=ap.parse_args()
    print('protocol,ell,p,slope_dlnC_dT')
    for ell in [int(x) for x in args.ells.split(',')]:
        cases=[
            ('fixed_local_with_greybody', ell+2.0),
            ('fixed_asymptotic_with_greybody', 1.0),
            ('fixed_local_no_barrier', 1.0),
        ]
        for name,p in cases:
            slope=-2.0*p*args.kappa
            print(f'{name},{ell},{p:.12g},{slope:.12g}')
    print('\nConclusion: mode-dependent p=l+2 requires fixed local frequency plus')
    print('low-frequency greybody filtering. The general law is protocol-aware:')
    print('the physical channel determines p, and geometry maps p to latency slope.')

if __name__=='__main__': main()
