"""Validation rung for HorizonLink's planned Unruh-DeWitt detector engine.

Before using a detector calculation to infer a near-horizon noise exponent, the
code must reproduce the exactly known stationary response of a linearly coupled
Unruh-DeWitt detector in 3+1 dimensional Minkowski vacuum under uniform proper
acceleration a (natural units):

    R_up(Omega,a) = Omega/(2*pi) / [exp(2*pi*Omega/a)-1], Omega>0.

The corresponding de-excitation rate includes spontaneous emission:

    R_down = Omega/(2*pi) * [1 + 1/(exp(2*pi*Omega/a)-1)].

Detailed balance must satisfy

    R_up/R_down = exp(-2*pi*Omega/a),

which identifies T_U=a/(2*pi).

This file is deliberately a benchmark, not a black-hole result. Any future
numerical Wightman-integral implementation must match these values before its
noise scaling is admitted into HorizonLink's discovery pipeline.
"""
from __future__ import annotations
import argparse, math


def occupation(Omega,a):
    z=2.0*math.pi*Omega/a
    return 1.0/math.expm1(z)

def rates(Omega,a):
    n=occupation(Omega,a)
    pref=Omega/(2.0*math.pi)
    return pref*n, pref*(1.0+n)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--gaps',default='0.25,0.5,1,2')
    ap.add_argument('--accelerations',default='0.5,1,2,5,10')
    args=ap.parse_args()
    print('Omega,a,T_Unruh,R_up,R_down,ratio,boltzmann,relative_error')
    worst=0.0
    for Om in [float(x) for x in args.gaps.split(',')]:
        for a in [float(x) for x in args.accelerations.split(',')]:
            up,down=rates(Om,a)
            ratio=up/down
            expected=math.exp(-2.0*math.pi*Om/a)
            err=abs(ratio-expected)/expected
            worst=max(worst,err)
            print(f'{Om:.12g},{a:.12g},{a/(2*math.pi):.12e},{up:.12e},{down:.12e},{ratio:.12e},{expected:.12e},{err:.3e}')
    print(f'worst_relative_error={worst:.3e}')
    if worst > 1e-12:
        raise SystemExit('FAIL: detailed-balance benchmark did not close')
    print('PASS: stationary UDW thermal benchmark closes to numerical precision.')
    print('NEXT: compare a numerical switched Wightman integral against this long-time limit.')

if __name__=='__main__': main()
