"""Finite-time Unruh-DeWitt benchmark with Gaussian switching.

This is the next validation layer before attempting Schwarzschild Wightman
functions.  It evaluates the response of a uniformly accelerated detector in
3+1 Minkowski vacuum using a smooth Gaussian switching function and the
stationary accelerated Wightman function.

For acceleration a,
  W(s) = -a^2/[16*pi^2*sinh^2(a(s-i eps)/2)].
For chi(tau)=exp[-tau^2/(2 sigma^2)], stationarity reduces the double integral to
  F(Omega) = sqrt(pi)*sigma * integral ds exp[-s^2/(4 sigma^2)]
                                      exp[-i Omega s] W(s).

Direct integration across the distributional singularity is numerically
fragile. We therefore subtract the inertial Wightman singularity analytically:
  DeltaW = W_acc - W_inertial,
which is finite at s=0 with DeltaW(0)=a^2/(48*pi^2).  The accelerated response
is reconstructed as
  F_acc = F_inertial + DeltaF.

The long-interaction detailed-balance target is
  F(+Omega)/F(-Omega) -> exp(-2*pi*Omega/a).
Finite sigma is expected to deviate because switching broadens the spectrum.

No black-hole capacity exponent is fitted here. Passing this benchmark is a
prerequisite for trusting later curved-spacetime detector noise calculations.
"""
from __future__ import annotations

import argparse
import math

try:
    from scipy.integrate import quad
except ImportError as exc:
    raise SystemExit("This benchmark requires scipy") from exc

PI = math.pi


def delta_wightman(s: float, a: float) -> float:
    z = 0.5 * a * s
    if abs(z) < 1.0e-4:
        # csch^2 z = z^-2 - 1/3 + z^2/15 - 2 z^4/189 + ...
        # W_acc-W_inertial = a^2/(48 pi^2) - a^4 s^2/(960 pi^2)+...
        return a*a/(48.0*PI*PI) - a**4*s*s/(960.0*PI*PI)
    w_acc = -(a*a)/(16.0*PI*PI*(math.sinh(z)**2))
    w_in = -1.0/(4.0*PI*PI*s*s)
    return w_acc - w_in


def inertial_gaussian_response(omega: float, sigma: float) -> float:
    # Spectral convolution of inertial UDW rate R(w)=-w Theta(-w)/(2pi)
    # with |chi_hat|^2. Overall normalization matches chi=exp(-tau^2/2sigma^2).
    # Numerically integrate a smooth positive-frequency variable u=-w >=0.
    pref = sigma*sigma
    integrand = lambda u: u * math.exp(-sigma*sigma*(omega+u)**2)
    val, _ = quad(integrand, 0.0, math.inf, epsabs=1e-12, epsrel=1e-10, limit=300)
    return pref * val


def response(omega: float, a: float, sigma: float) -> float:
    fin = inertial_gaussian_response(omega, sigma)
    pref = math.sqrt(PI)*sigma
    # DeltaW is even and real, so use cosine transform.
    def integrand(s: float) -> float:
        return math.exp(-s*s/(4.0*sigma*sigma))*math.cos(omega*s)*delta_wightman(s,a)
    cutoff = max(12.0*sigma, 40.0/a)
    corr, _ = quad(integrand, 0.0, cutoff, epsabs=1e-11, epsrel=1e-9, limit=500)
    return fin + 2.0*pref*corr


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--a',type=float,default=1.0)
    ap.add_argument('--omega',type=float,default=0.5)
    ap.add_argument('--sigmas',default='0.5,1,2,4,8,16')
    args=ap.parse_args()
    target=math.exp(-2.0*PI*args.omega/args.a)
    print('sigma,F_exc,F_deexc,ratio,target,relative_error')
    for sigma in [float(x) for x in args.sigmas.split(',')]:
        up=response(+args.omega,args.a,sigma)
        down=response(-args.omega,args.a,sigma)
        ratio=up/down
        rel=abs(ratio-target)/target
        print(f'{sigma:.12g},{up:.12e},{down:.12e},{ratio:.12e},{target:.12e},{rel:.12e}')
    print('\nExpected: as sigma*a grows, the ratio approaches exp(-2*pi*Omega/a).')
    print('Failure to converge means the regularization/normalization must be fixed before Schwarzschild work.')

if __name__=='__main__':
    main()
