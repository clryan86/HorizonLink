"""Test a generic non-extremal horizon information-delay cancellation.

For a static metric ds^2=-f(r)dt^2+dr^2/f(r)+..., let x=r-r_h and
f(x)=a*x+b*x^2+..., where a=2*kappa in geometric units (c=1).

A static emitter to fixed receiver has g^2 proportional to f. In the low-SNR
AWGN limit C proportional to SNR proportional to g^2, hence ln C = ln f+const.
An outgoing radial null ray has escape time T = integral_x^X dx/f(x), so
T = -(1/a) ln x + const + O(x).

Therefore Q = ln C + a*T = ln C + 2*kappa*T has a finite horizon limit.
This is the surface-gravity form of HorizonLink's Schwarzschild combination.

This script tests robustness to arbitrary quadratic/cubic near-horizon metric
coefficients. It also demonstrates why extremal horizons (a=0) are a separate
universality class.
"""
from __future__ import annotations
import argparse, math


def f(x: float, a: float, b: float, d: float) -> float:
    return a*x+b*x*x+d*x*x*x


def integrate_escape(x0: float, x1: float, a: float, b: float, d: float, n: int=200000) -> float:
    # logarithmic midpoint quadrature resolves the horizon singularity.
    u0,u1=math.log(x0),math.log(x1)
    du=(u1-u0)/n
    total=0.0
    for i in range(n):
        u=u0+(i+0.5)*du
        x=math.exp(u)
        total += x/f(x,a,b,d)*du
    return total


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--a',type=float,default=0.7,help='f prime at horizon = 2*kappa')
    p.add_argument('--b',type=float,default=-0.13)
    p.add_argument('--d',type=float,default=0.021)
    p.add_argument('--x-receiver',type=float,default=0.2)
    args=p.parse_args()
    if args.a <= 0: raise SystemExit('Use a>0 for non-extremal test; a=0 is extremal class.')
    print('epsilon,Q,delta_Q,delta_Q/epsilon')
    qs=[]
    for k in range(2,9):
        x=10.0**(-k)
        C=f(x,args.a,args.b,args.d) # multiplicative constants cancel from residuals
        T=integrate_escape(x,args.x_receiver,args.a,args.b,args.d)
        Q=math.log(C)+args.a*T
        qs.append((x,Q))
    qlim=qs[-1][1]
    for x,Q in qs:
        dq=Q-qlim
        print(f'{x:.1e},{Q:.15g},{dq:.12e},{dq/x:.12e}')
    print('\nPrediction: Q approaches a finite constant for every smooth simple-zero horizon.')
    print('Coefficient is a=2*kappa; Schwarzschild is one member of this class.')
    print('Extremal horizons have a=0/double zero and should fail this logarithmic cancellation.')

if __name__=='__main__': main()
