"""Test whether HorizonLink's exponent law survives full Shannon capacity.

No low-SNR approximation is used to construct capacity:
    C(x) = B * log2(1 + SNR0*x^p)
with non-extremal horizon latency
    T(x) = T0 - ln(x)/(2*kappa) + O(x).

For any finite SNR0 and p>0, x->0 forces SNR->0 automatically, so the exact
Shannon expression must asymptotically recover
    d ln C / dT -> -2*p*kappa.

This experiment measures the slope numerically over progressively deeper
near-horizon windows and across many bandwidth/SNR choices. It also records the
pre-asymptotic deviation, which is operationally important.
"""
from __future__ import annotations
import argparse, math


def capacity(B,snr):
    return B*math.log1p(snr)/math.log(2.0)

def slope(xs,ys):
    xm=sum(xs)/len(xs); ym=sum(ys)/len(ys)
    return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)**2 for x in xs)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kappa',type=float,default=0.25)
    ap.add_argument('--powers',default='1,2,3,4')
    ap.add_argument('--snr0s',default='0.01,1,100,1000000')
    ap.add_argument('--bandwidths',default='1,1000000')
    args=ap.parse_args()
    windows=[[-1,-2,-3,-4],[-3,-4,-5,-6],[-5,-6,-7,-8],[-7,-8,-9,-10]]
    print('p,snr0,B,window_min_exp,window_max_exp,measured,predicted,rel_error')
    for p in [float(v) for v in args.powers.split(',')]:
      target=-2*p*args.kappa
      for snr0 in [float(v) for v in args.snr0s.split(',')]:
       for B in [float(v) for v in args.bandwidths.split(',')]:
        for exps in windows:
            Ts=[]; lnCs=[]
            for e in exps:
                x=10.0**e
                snr=snr0*(x**p)
                C=capacity(B,snr)
                T=-math.log(x)/(2*args.kappa)+0.2+0.3*x
                Ts.append(T); lnCs.append(math.log(C))
            m=slope(Ts,lnCs)
            rel=abs((m-target)/target)
            print(f'{p:.6g},{snr0:.6g},{B:.6g},{min(exps)},{max(exps)},{m:.12e},{target:.12e},{rel:.12e}')
    print('\nPrediction: for every finite SNR0 and B, deeper windows converge to -2*p*kappa.')
    print('Bandwidth changes ln(C) by an additive constant and cannot change the asymptotic slope.')
    print('Large SNR0 can delay the onset of the asymptotic regime but cannot remove it for p>0.')

if __name__=='__main__': main()
