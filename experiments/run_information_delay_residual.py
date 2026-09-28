"""Numerically test the low-SNR Schwarzschild information-delay asymptote.

For epsilon=(r-rs)/rs << 1, g^2=epsilon/(1+epsilon) ~ epsilon.
With fixed reference SNR rho and AWGN capacity C=B log2(1+rho*g^2),
low SNR gives C ~ B*rho*epsilon/ln(2), hence ln C ~ ln epsilon + const.
The outgoing Schwarzschild delay contains -tau*ln epsilon, tau=rs/c.
Therefore Q = ln(C) + t/tau should approach a constant.

This is an internal consistency/asymptotic scaling result of the stated model,
not a claim of communication through an event horizon or new fundamental law.
"""
from __future__ import annotations
import argparse, math
from horizonlink.horizons.schwarzschild import C as LIGHT_SPEED, M_SUN, coordinate_escape_delay, gravitational_redshift_factor, schwarzschild_radius

def awgn_capacity(bw, snr):
    return bw * math.log1p(snr) / math.log(2.0)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mass-solar',type=float,default=30.0)
    p.add_argument('--receiver-rs',type=float,default=100.0)
    p.add_argument('--bandwidth-hz',type=float,default=1e6)
    p.add_argument('--far-snr',type=float,default=100.0)
    p.add_argument('--decades',type=int,default=7)
    a=p.parse_args()
    mass=a.mass_solar*M_SUN; rs=schwarzschild_radius(mass); tau=rs/LIGHT_SPEED
    # From exact delay expression with r1=R*rs and epsilon->0:
    # t/tau = (R-1-epsilon) + ln(R-1) - ln(epsilon)
    # ln C = ln(B*rho/ln2) + ln(epsilon) + o(1)
    q_limit=(a.receiver_rs-1.0)+math.log(a.receiver_rs-1.0)+math.log(a.bandwidth_hz*a.far_snr/math.log(2.0))
    print(f'analytic_Q_limit={q_limit:.15g}')
    print('k,epsilon,capacity_bps,delay_s,Q,residual,relative_residual')
    for k in range(1,a.decades+1):
        eps=10.0**(-2*k); r0=rs*(1+eps)
        if r0==rs: break
        g=gravitational_redshift_factor(mass,r0)
        cap=awgn_capacity(a.bandwidth_hz,a.far_snr*g*g)
        delay=coordinate_escape_delay(mass,r0,a.receiver_rs*rs)
        q=math.log(cap)+delay/tau
        residual=q-q_limit
        print(f'{k},{eps:.6e},{cap:.12e},{delay:.12e},{q:.15g},{residual:.12e},{residual/q_limit:.12e}')

if __name__=='__main__': main()
