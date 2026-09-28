"""Observer-noise universality-class stress test for HorizonLink.

This deliberately does NOT claim a complete Unruh-DeWitt response calculation.
It tests the asymptotic consequence of two physically distinct detector classes:

1. Static detector held near a non-extremal Schwarzschild horizon in a thermal
   equilibrium state. Tolman temperature scales T_loc ~ f^(-1/2). For fixed
   local detector gap in the high-temperature limit, occupation/noise scales
   N ~ f^(-1/2), hence b=-1/2.

2. Regular freely falling detector class. A regular horizon-crossing response
   is represented by finite nonzero noise N -> const, hence b=0. This is the
   conservative scaling statement; the detailed finite response depends on
   state, trajectory, switching and detector gap.

If received signal scales S~f^a, exact Shannon capacity with SNR=S/N predicts
q=a-b when q>0, and near a non-extremal horizon
    d ln C / dT -> -2 q kappa.

Thus observer choice changes q even with identical signal scaling. The script
uses the exact Shannon expression and numerically measures the asymptotic slope.
"""
from __future__ import annotations
import argparse, math


def C_shannon(B,snr):
    return B*math.log1p(snr)/math.log(2.0)

def slope(xs,ys):
    xm=sum(xs)/len(xs); ym=sum(ys)/len(ys)
    return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)**2 for x in xs)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--a',type=float,default=1.0,help='signal exponent S~f^a')
    ap.add_argument('--kappa',type=float,default=0.25)
    ap.add_argument('--B',type=float,default=1.0)
    ap.add_argument('--S0',type=float,default=1.0)
    ap.add_argument('--N0',type=float,default=1.0)
    args=ap.parse_args()
    fs=[1e-3,1e-5,1e-7,1e-9,1e-11]
    classes=[('static_tolman',-0.5),('regular_freefall',0.0)]
    print('observer,b,q,f,snr,capacity,T')
    for name,b in classes:
        Ts=[]; lCs=[]
        for ff in fs:
            S=args.S0*ff**args.a
            N=args.N0*ff**b
            snr=S/N
            cap=C_shannon(args.B,snr)
            # f is linear in horizon distance at leading order; additive
            # constants in T do not affect the logarithmic slope.
            T=-math.log(ff)/(2.0*args.kappa)
            Ts.append(T); lCs.append(math.log(cap))
            print(f'{name},{b:.6g},{args.a-b:.6g},{ff:.3e},{snr:.12e},{cap:.12e},{T:.12e}')
        measured=slope(Ts[-3:],lCs[-3:])
        q=args.a-b
        target=-2.0*q*args.kappa if q>0 else 0.0
        print(f'# {name}: measured={measured:.12g} target={target:.12g} q={q:.12g}')
        print()
    print('For a=1 and kappa=1/4:')
    print(' static Tolman class predicts q=3/2 and slope=-3*kappa=-0.75.')
    print(' regular free-fall class predicts q=1 and slope=-2*kappa=-0.5.')
    print('A full detector calculation should replace these class assumptions next.')

if __name__=='__main__': main()
