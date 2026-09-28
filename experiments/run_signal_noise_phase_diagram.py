"""Generalize HorizonLink to horizon-dependent signal AND noise.

Let received signal power S ~ S0*x^a and effective noise power N ~ N0*x^b,
with x=r-r_h -> 0+ near a non-extremal horizon. Then

    SNR ~ (S0/N0) * x^(a-b).

Define q=a-b. Exact Shannon capacity C=B log2(1+SNR) gives three distinct
asymptotic classes:

q>0: SNR->0, C~const*x^q, so d ln C/dT -> -2*q*kappa.
q=0: SNR->constant, C->constant, so d ln C/dT -> 0.
q<0: SNR->infinity, C~B*|q|*|ln x|/ln2. Since T~|ln x|/(2*kappa),
     C grows only linearly with T and d ln C/dT -> 0 (roughly 1/T), not a
     positive constant.

Thus the simple exponent law applies to the signal-losing phase q>0. The
boundary q=0 is a channel phase boundary. This script measures all three using
full Shannon capacity rather than a low-SNR approximation.
"""
from __future__ import annotations
import argparse, math


def cap(B,snr): return B*math.log1p(snr)/math.log(2.0)
def local_slope(x1,y1,x2,y2): return (y2-y1)/(x2-x1)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kappa',type=float,default=0.25)
    ap.add_argument('--pairs',default='2:0,2:1,2:2,1:2,0:2')
    ap.add_argument('--s0',type=float,default=3.0)
    ap.add_argument('--n0',type=float,default=1.0)
    ap.add_argument('--B',type=float,default=1e6)
    args=ap.parse_args()
    eps=[1e-3,1e-5,1e-7,1e-9,1e-11]
    print('a,b,q,x,snr,capacity,T,dlnC_dT_local,target_if_q_positive')
    for pair in args.pairs.split(','):
        a,b=[float(v) for v in pair.split(':')]; q=a-b
        prev=None
        for x in eps:
            snr=(args.s0/args.n0)*(x**q)
            C=cap(args.B,snr)
            T=-math.log(x)/(2*args.kappa)
            sl=float('nan') if prev is None else local_slope(prev[0],prev[1],T,math.log(C))
            target=-2*q*args.kappa if q>0 else 0.0
            print(f'{a:.6g},{b:.6g},{q:.6g},{x:.3e},{snr:.12e},{C:.12e},{T:.12e},{sl:.12e},{target:.12e}')
            prev=(T,math.log(C))
        print()
    print('Phase diagram:')
    print(' q>0  capacity vanishes exponentially in latency; slope -> -2 q kappa.')
    print(' q=0  capacity approaches a nonzero constant; logarithmic slope -> 0.')
    print(' q<0  idealized SNR diverges; capacity grows ~T, but logarithmic slope -> 0.')
    print('Physical noise models determine b; no claim is made here that Hawking noise has a specific b.')

if __name__=='__main__': main()
