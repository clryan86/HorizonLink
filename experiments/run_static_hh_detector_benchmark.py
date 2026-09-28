"""Schwarzschild static-detector Hartle-Hawking benchmark for HorizonLink.

This is an analytic/numerical bridge before a full Schwarzschild mode-sum
Wightman implementation. Literature establishes that a static UDW detector in
the Hartle-Hawking state is thermal at the local Tolman-redshifted Hawking
temperature.

G=c=hbar=kB=M=1:
  f(r)=1-2/r,  kappa=1/4,  T_H=kappa/(2*pi),
  T_local=T_H/sqrt(f).

For detector gap Omega, detailed balance predicts
  R_up/R_down = exp[-Omega/T_local].

Near the horizon f->0, T_local diverges and the ratio tends to one.  This file
also measures the leading approach 1-ratio ~ sqrt(f), a directly checkable
near-horizon exponent that later mode-sum code must reproduce without being
handed the Tolman formula.

This benchmark is NOT the full detector calculation and must not be used as
independent evidence for a new result.
"""
from __future__ import annotations
import argparse, math

PI=math.pi

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--omega',type=float,default=0.5)
    ap.add_argument('--eps',default='1e-2,1e-3,1e-4,1e-5,1e-6,1e-7,1e-8')
    args=ap.parse_args()
    kappa=0.25
    TH=kappa/(2*PI)
    xs=[]; deficits=[]
    print('epsilon,f,T_local,ratio,one_minus_ratio')
    for eps in [float(x) for x in args.eps.split(',')]:
        r=2*(1+eps)
        ff=1-2/r
        Tloc=TH/math.sqrt(ff)
        ratio=math.exp(-args.omega/Tloc)
        deficit=1-ratio
        xs.append(ff); deficits.append(deficit)
        print(f'{eps:.12e},{ff:.12e},{Tloc:.12e},{ratio:.12e},{deficit:.12e}')
    # Fit only the deepest four points: log(1-ratio) ~ alpha log f + const.
    lx=[math.log(x) for x in xs[-4:]]; ly=[math.log(y) for y in deficits[-4:]]
    xm=sum(lx)/len(lx); ym=sum(ly)/len(ly)
    alpha=sum((x-xm)*(y-ym) for x,y in zip(lx,ly))/sum((x-xm)**2 for x in lx)
    print(f'\nnear_horizon_deficit_exponent={alpha:.12g}')
    print('target exponent = 0.5')
    print('Future full mode-sum detector code must recover this static HH benchmark independently.')

if __name__=='__main__': main()
