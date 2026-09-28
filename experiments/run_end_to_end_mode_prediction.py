"""End-to-end HorizonLink prediction test using numerically derived greybody factors.

Goal: do not insert the final capacity exponent. For each emitter position x,
compute its gravitationally redshifted asymptotic carrier frequency, solve the
Schwarzschild scalar wave equation for the corresponding greybody factor,
build a low-SNR capacity proxy, compute the outgoing latency, and then measure
slope d ln(C)/dT from held-out near-horizon points.

Operational setup (G=c=M=1):
- Schwarzschild horizon r_h=2, kappa=1/4.
- Static transmitter holds fixed local angular frequency omega_local.
- omega_inf = sqrt(f(r0))*omega_local.
- received signal/SNR proxy = f(r0)*Gamma_l(omega_inf).
- low-SNR Shannon capacity is proportional to that proxy, so normalization is
  irrelevant to d ln C/dT.
- outgoing coordinate latency to fixed r_recv is r_*(r_recv)-r_*(r0).

Independent prediction from the low-frequency scalar barrier is
Gamma_l ~ omega^(2l+2), hence slope -> -2(l+2)kappa. The numerical measurement
below never uses that exponent when constructing C.
"""
from __future__ import annotations
import argparse, cmath, math


def f(r): return 1.0-2.0/r

def tortoise(r): return r+2.0*math.log(r/2.0-1.0)

def V(r,l):
    fr=f(r)
    return fr*(l*(l+1.0)/(r*r)+2.0/(r**3))

def deriv(r,psi,y,w,l):
    fr=f(r)
    return y/fr, -(w*w-V(r,l))*psi/fr

def rk4(r,psi,y,h,w,l):
    a,b=deriv(r,psi,y,w,l)
    c,d=deriv(r+h/2,psi+h*a/2,y+h*b/2,w,l)
    e,g=deriv(r+h/2,psi+h*c/2,y+h*d/2,w,l)
    q,s=deriv(r+h,psi+h*e,y+h*g,w,l)
    return psi+h*(a+2*c+2*e+q)/6, y+h*(b+2*d+2*g+s)/6

def greybody(w,l):
    r=2.0*(1.0+1e-5)
    rmax=max(250.0,25.0/w)
    rs=tortoise(r)
    psi=cmath.exp(-1j*w*rs)
    y=-1j*w*psi
    while r<rmax:
        h=min(0.03,max(1e-6,0.12*(r-2.0)),rmax-r)
        psi,y=rk4(r,psi,y,h,w,l)
        r+=h
    rs=tortoise(r)
    em=cmath.exp(-1j*w*rs)
    ain=(psi-y/(1j*w))/(2.0*em)
    return 1.0/(abs(ain)**2)

def regression_slope(xs,ys):
    xm=sum(xs)/len(xs); ym=sum(ys)/len(ys)
    return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)**2 for x in xs)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ells',default='0,1,2')
    ap.add_argument('--eps',default='1e-2,5e-3,2e-3,1e-3')
    ap.add_argument('--omega-local',type=float,default=0.7)
    ap.add_argument('--receiver-r',type=float,default=100.0)
    args=ap.parse_args()
    kappa=0.25
    eps=[float(x) for x in args.eps.split(',')]
    print('ell,epsilon,omega_inf,Gamma,capacity_proxy,latency')
    for l in [int(x) for x in args.ells.split(',')]:
        Ts=[]; lnCs=[]
        for e in eps:
            r0=2.0*(1.0+e)
            fr=f(r0)
            winf=args.omega_local*math.sqrt(fr)
            gamma=greybody(winf,l)
            C=fr*gamma
            T=tortoise(args.receiver_r)-tortoise(r0)
            Ts.append(T); lnCs.append(math.log(C))
            print(f'{l},{e:.12e},{winf:.12e},{gamma:.12e},{C:.12e},{T:.12e}')
        measured=regression_slope(Ts,lnCs)
        predicted=-2.0*(l+2.0)*kappa
        rel=abs((measured-predicted)/predicted)
        print(f'# ell={l} measured={measured:.12g} predicted={predicted:.12g} rel_error={rel:.6g}')
        print()
    print('A successful asymptotic test approaches predicted=-2(l+2)kappa as the')
    print('emitter positions move closer to the horizon and omega_inf enters the')
    print('low-frequency greybody regime. Finite-distance deviations are expected.')

if __name__=='__main__': main()
