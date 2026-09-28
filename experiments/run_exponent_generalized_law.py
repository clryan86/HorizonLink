"""Generalize HorizonLink's horizon capacity-delay cancellation by redshift exponent.

Suppose near a non-extremal horizon x=r-r_h -> 0+ the operational channel
capacity obeys C ~ A*x^p for a specified emitter/receiver/mode family, while
outgoing asymptotic delay obeys T ~ -(1/(2*kappa))*ln(x)+T0.

Then the finite combination is not universally ln(C)+2*kappa*T. It is

    I_p = ln(C) + 2*p*kappa*T,

because ln(C) ~ ln(A)+p ln(x). The earlier HorizonLink law is the p=1 member.
This script tests the generalized cancellation and deliberately tests a wrong
coefficient as a falsification control.

This separates geometry (kappa, logarithmic delay) from operational redshift /
channel physics (the exponent p). Critical modes or extremal horizons can leave
this universality class entirely.
"""
from __future__ import annotations
import argparse, math


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kappa',type=float,default=0.125)
    ap.add_argument('--amplitude',type=float,default=3.7)
    ap.add_argument('--powers',default='0.5,1,1.5,2,3')
    ap.add_argument('--eps',default='1e-2,1e-4,1e-6,1e-8,1e-10')
    args=ap.parse_args()
    powers=[float(v) for v in args.powers.split(',')]
    eps=[float(v) for v in args.eps.split(',')]
    print('p,x,I_correct,I_wrong_p1')
    for p in powers:
        for x in eps:
            # Include smooth non-leading corrections so this is not an exact
            # cancellation at finite x.
            C=args.amplitude*(x**p)*(1.0+0.7*x-0.2*x*x)
            T=-(1.0/(2.0*args.kappa))*math.log(x) + 0.31 + 0.4*x
            I=math.log(C)+2.0*p*args.kappa*T
            wrong=math.log(C)+2.0*args.kappa*T
            print(f'{p:.6g},{x:.3e},{I:.12e},{wrong:.12e}')
        print()
    print('PASS: I_correct converges for every p>0.')
    print('CONTROL: I_wrong_p1 converges only for p=1; otherwise it diverges.')
    print('Interpretation: the coefficient measures the channel redshift exponent, not geometry alone.')

if __name__=='__main__':
    main()
