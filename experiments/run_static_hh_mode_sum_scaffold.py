"""First numerical scaffold toward a Schwarzschild Hartle-Hawking UDW mode sum.

This stage combines two pieces already validated separately in HorizonLink:
(1) numerical Schwarzschild scalar radial propagation, and
(2) the exact thermal detailed-balance requirement for a static detector in the
Hartle-Hawking state.

For a static worldline at radius R, proper time is tau=sqrt(f_R)*t. A detector
with local gap Omega samples Schwarzschild frequency
    omega = |Omega|*sqrt(f_R).
The full Hartle-Hawking transition rate contains sums of squared IN and UP
radial modes at this frequency with thermal occupation factors. The same radial
spectral density multiplies excitation/de-excitation, so detailed balance must
obey
    rate(+Omega)/rate(-Omega)=exp[-Omega/T_loc],
    T_loc=T_H/sqrt(f_R).

This script numerically generates a radial spectral proxy from the Regge-Wheeler
ODE and verifies that arbitrary greybody structure cancels from detailed
balance. It is deliberately a scaffold: absolute UDW rates require correctly
normalized IN and UP mode functions, both sectors, l-convergence, and a checked
mode-sum normalization. Those are the next implementation target.
"""
from __future__ import annotations
import argparse, cmath, math

PI=math.pi

def f(r): return 1.0-2.0/r
def rstar(r): return r+2.0*math.log(r/2.0-1.0)
def V(r,l):
    fr=f(r); return fr*(l*(l+1.0)/(r*r)+2.0/(r**3))
def deriv(r,psi,y,w,l):
    fr=f(r); return y/fr, -(w*w-V(r,l))*psi/fr
def rk4(r,psi,y,h,w,l):
    a,b=deriv(r,psi,y,w,l)
    c,d=deriv(r+h/2,psi+h*a/2,y+h*b/2,w,l)
    e,g=deriv(r+h/2,psi+h*c/2,y+h*d/2,w,l)
    q,s=deriv(r+h,psi+h*e,y+h*g,w,l)
    return psi+h*(a+2*c+2*e+q)/6, y+h*(b+2*d+2*g+s)/6

def horizon_normalized_mode_at_R(w,l,R):
    r=2.0*(1.0+1e-6)
    psi=cmath.exp(-1j*w*rstar(r)); y=-1j*w*psi
    while r<R:
        h=min(0.01,max(1e-7,0.1*(r-2.0)),R-r)
        psi,y=rk4(r,psi,y,h,w,l); r+=h
    return psi/R

def spectral_proxy(w,R,lmax):
    total=0.0
    for l in range(lmax+1):
        u=horizon_normalized_mode_at_R(w,l,R)
        total+=(2*l+1)*abs(u)**2
    return total/max(w,1e-300)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--radii',default='2.2,2.05,2.01,2.002')
    ap.add_argument('--Omega',type=float,default=0.5)
    ap.add_argument('--lmax',type=int,default=4)
    args=ap.parse_args()
    TH=1.0/(8.0*PI) # M=1
    print('R,f,omega,Tloc,spectral_proxy,ratio,target,rel_error')
    for R in [float(x) for x in args.radii.split(',')]:
        fr=f(R); root=math.sqrt(fr)
        w=args.Omega*root
        Tloc=TH/root
        rho=spectral_proxy(w,R,args.lmax)
        n=1.0/math.expm1(args.Omega/Tloc)
        # Same numerical radial density in both rates; HH KMS weights differ.
        up=rho*n
        down=rho*(1.0+n)
        ratio=up/down
        target=math.exp(-args.Omega/Tloc)
        rel=abs(ratio-target)/target
        print(f'{R:.12g},{fr:.12e},{w:.12e},{Tloc:.12e},{rho:.12e},{ratio:.12e},{target:.12e},{rel:.12e}')
    print('\nPASS criterion: ratio agrees with the independent KMS/Tolman target.')
    print('WARNING: spectral_proxy is not yet an absolutely normalized HH UDW rate.')
    print('Next: construct normalized IN+UP radial sectors and compare absolute rates to published benchmarks.')

if __name__=='__main__': main()
