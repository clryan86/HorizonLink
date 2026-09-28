"""Blind recovery test for the HorizonLink capacity-delay slope law.

Goal: do not supply the redshift/capacity exponent p to the predictor.
Generate (or later ingest) capacity-vs-horizon-distance data, infer p from one
subset, then predict the independently fitted slope d ln(C)/dT on held-out data.

For a non-extremal stationary horizon:
    T ~ -(1/(2 kappa)) ln x + const
If C ~ A x^p times smooth corrections, the prediction is
    d ln C / dT -> -2 p kappa.

This script uses deterministic synthetic controls first. The same estimator is
intended to be fed numerical wave/greybody data next.
"""
from __future__ import annotations
import argparse, math


def linfit(x, y):
    n=len(x); xb=sum(x)/n; yb=sum(y)/n
    sxx=sum((v-xb)**2 for v in x)
    sxy=sum((a-xb)*(b-yb) for a,b in zip(x,y))
    m=sxy/sxx
    b=yb-m*xb
    rss=sum((yy-(m*xx+b))**2 for xx,yy in zip(x,y))
    return m,b,rss


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kappa',type=float,default=0.137)
    ap.add_argument('--powers',default='0.5,1,1.5,2,3')
    args=ap.parse_args()
    xs=[10.0**(-k) for k in range(2,13)]
    print('true_p,inferred_p,predicted_slope,heldout_slope,relative_error')
    for ptrue in [float(v) for v in args.powers.split(',')]:
        # Smooth finite-distance corrections deliberately obscure the exact law.
        C=[2.31*x**ptrue*(1+0.83*x+0.17*x*x) for x in xs]
        T=[-(1/(2*args.kappa))*math.log(x)+0.41+0.29*x for x in xs]
        # Infer p only from alternating near-horizon samples using ln C vs ln x.
        train=list(range(4,len(xs),2))
        test=list(range(5,len(xs),2))
        p_hat,_,_=linfit([math.log(xs[i]) for i in train],[math.log(C[i]) for i in train])
        predicted=-2*p_hat*args.kappa
        measured,_,_=linfit([T[i] for i in test],[math.log(C[i]) for i in test])
        err=abs((measured-predicted)/measured)
        print(f'{ptrue:.8g},{p_hat:.12e},{predicted:.12e},{measured:.12e},{err:.12e}')

    print('\nSuccess criterion: inferred p predicts held-out d ln(C)/dT without fitting that slope directly.')
    print('Next: replace synthetic C(x) with independently computed wave/greybody transmission data.')

if __name__=='__main__': main()
