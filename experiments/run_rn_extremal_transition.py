"""Reissner-Nordstrom stress test for the HorizonLink horizon information-delay law.

Geometric units G=c=1.  For RN,
  f(r)=1-2M/r+Q^2/r^2=(r-r+)(r-r-)/r^2
  r+ = M + sqrt(M^2-Q^2)
  r- = M - sqrt(M^2-Q^2)
  kappa=(r+-r-)/(2 r+^2)

For a static emitter, take received low-SNR capacity C proportional to f(r0).
For an outgoing radial null ray, coordinate travel time is integral dr/f(r).
The candidate non-extremal quantity is H = ln C + 2*kappa*T.

This script tests:
1. finite H as r0 -> r+ for every Q<M;
2. convergence rate as Q approaches M;
3. failure/change of universality at Q=M, where kappa=0 and the horizon is a double zero.

This is a mathematical model test, not a claim of empirical discovery.
"""
from __future__ import annotations

import math


def horizons(M: float, Q: float):
    d=math.sqrt(max(0.0,M*M-Q*Q))
    return M+d, M-d


def f_rn(r: float,M: float,Q: float)->float:
    return 1.0-2.0*M/r+(Q*Q)/(r*r)


def kappa_rn(M: float,Q: float)->float:
    rp,rm=horizons(M,Q)
    return (rp-rm)/(2.0*rp*rp)


def tortoise_nonext(r: float,M: float,Q: float)->float:
    rp,rm=horizons(M,Q)
    gap=rp-rm
    return r + (rp*rp/gap)*math.log(abs(r-rp)) - (rm*rm/gap)*math.log(abs(r-rm))


def travel_nonext(r0: float,r1: float,M: float,Q: float)->float:
    return tortoise_nonext(r1,M,Q)-tortoise_nonext(r0,M,Q)


def extremal_tortoise(r: float,M: float)->float:
    # integral dr/(1-M/r)^2 = r + 2M ln(r-M) - M^2/(r-M), up to constant
    x=r-M
    return r+2.0*M*math.log(abs(x))-M*M/x


def main():
    M=1.0
    charge_fracs=[0.0,0.5,0.9,0.99,0.999,0.9999]
    epsilons=[1e-2,1e-4,1e-6,1e-8,1e-10]
    print('NON-EXTREMAL RN')
    print('q_over_m,kappa,epsilon,H')
    for qf in charge_fracs:
        Q=qf*M
        rp,_=horizons(M,Q)
        kap=kappa_rn(M,Q)
        r1=100.0*rp
        for eps in epsilons:
            r0=rp*(1.0+eps)
            C=f_rn(r0,M,Q)
            T=travel_nonext(r0,r1,M,Q)
            H=math.log(C)+2.0*kap*T
            print(f'{qf:.6f},{kap:.12e},{eps:.1e},{H:.12e}')
        print()

    print('EXTREMAL RN (Q=M): candidate kappa law must fail because kappa=0')
    Q=M
    rp=M
    r1=100.0*M
    print('epsilon,lnC,T,lnC_plus_2kappaT')
    for eps in epsilons:
        r0=rp*(1.0+eps)
        C=f_rn(r0,M,Q)
        T=extremal_tortoise(r1,M)-extremal_tortoise(r0,M)
        print(f'{eps:.1e},{math.log(C):.12e},{T:.12e},{math.log(C):.12e}')

    print('\nPrediction: for Q<M, H tends to a finite Q-dependent constant as epsilon->0.')
    print('At Q=M, kappa=0 while ln C -> -infinity and T diverges ~1/(r-M), so the')
    print('non-extremal logarithmic cancellation changes universality class.')

if __name__=='__main__':
    main()
