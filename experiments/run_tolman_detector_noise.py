"""Replace phenomenological noise exponents with a concrete thermal detector model.

For a static detector outside Schwarzschild in the Hartle-Hawking state, the
local temperature obeys Tolman redshift:

    T_loc = T_H / sqrt(f),  f=1-2M/r.

For a fixed LOCAL detector gap Omega, the Bose occupation is

    n_th = 1/(exp(Omega/T_loc)-1).

As f -> 0, T_loc -> infinity and n_th ~ T_loc/Omega ~ f^(-1/2).
Thus this specific detector/noise proxy has noise exponent b=-1/2 when
N ~ n_th. Combining it with a signal power S ~ f^a gives

    SNR ~ f^(a+1/2),

so the near-horizon Shannon-capacity exponent is q=a+1/2 and

    d ln C/dT -> -2 q kappa

for a non-extremal horizon, provided the chosen detector model and noise proxy
are appropriate.

This is deliberately state/observer specific. It must NOT be generalized to
free-fall observers, the Boulware state, arbitrary detector gaps, or all notions
of communication noise.
"""
from __future__ import annotations
import argparse, math


def occupation(z):
    # z=Omega/T. Stable for z small/large.
    if z > 700: return 0.0
    return 1.0/math.expm1(z)

def slope(xs,ys):
    xm=sum(xs)/len(xs); ym=sum(ys)/len(ys)
    return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)**2 for x in xs)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--a',type=float,default=1.0,help='signal exponent S~f^a')
    ap.add_argument('--omega-over-TH',type=float,default=10.0)
    ap.add_argument('--kappa',type=float,default=0.25)
    ap.add_argument('--snr-scale',type=float,default=1.0)
    ap.add_argument('--B',type=float,default=1e6)
    args=ap.parse_args()
    fs=[1e-2,1e-4,1e-6,1e-8,1e-10]
    Ts=[]; lnCs=[]; lnf=[]; lnN=[]
    print('f,Tloc_over_TH,nthermal,signal,snr,capacity,latency')
    for f in fs:
        Tloc_over_TH=1.0/math.sqrt(f)
        z=args.omega_over_TH/Tloc_over_TH
        nth=occupation(z)
        signal=f**args.a
        # Use thermal occupation as the additive-noise proxy.
        snr=args.snr_scale*signal/max(nth,1e-300)
        C=args.B*math.log1p(snr)/math.log(2.0)
        T=-math.log(f)/(2.0*args.kappa)
        print(f'{f:.3e},{Tloc_over_TH:.12e},{nth:.12e},{signal:.12e},{snr:.12e},{C:.12e},{T:.12e}')
        Ts.append(T); lnCs.append(math.log(C)); lnf.append(math.log(f)); lnN.append(math.log(nth))
    b_fit=slope(lnf[-3:],lnN[-3:])
    measured=slope(Ts[-3:],lnCs[-3:])
    q_pred=args.a+0.5
    target=-2.0*q_pred*args.kappa
    print(f'noise_exponent_fit={b_fit:.12g} expected=-0.5')
    print(f'q_pred={q_pred:.12g}')
    print(f'dlnC_dT_measured={measured:.12g} target={target:.12g}')
    print('Caution: this result is for a static detector, Hartle-Hawking thermal response,')
    print('fixed local gap, and N proportional to thermal occupation only.')

if __name__=='__main__': main()
