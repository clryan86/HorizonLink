"""Search for near-horizon information/latency scaling laws.

This experiment combines the Schwarzschild redshift and escape-delay model with
simple AWGN Shannon capacity. It tests several normalizations rather than
assuming an invariant exists.

Important: this is an exterior, idealized channel model. It does not model
communication from inside an event horizon.
"""
from __future__ import annotations

import argparse
import math

from horizonlink.horizons.schwarzschild import C, M_SUN, coordinate_escape_delay, gravitational_redshift_factor, schwarzschild_radius


def capacity_awgn(bandwidth_hz: float, snr_linear: float) -> float:
    return bandwidth_hz * math.log2(1.0 + max(0.0, snr_linear))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--mass-solar", type=float, default=30.0)
    p.add_argument("--receiver-rs", type=float, default=100.0)
    p.add_argument("--bandwidth-hz", type=float, default=1e6)
    p.add_argument("--far-snr", type=float, default=100.0,
                   help="Reference linear SNR before gravitational power loss")
    p.add_argument("--decades", type=int, default=7)
    args = p.parse_args()

    mass = args.mass_solar * M_SUN
    rs = schwarzschild_radius(mass)
    r_end = args.receiver_rs * rs
    tau = rs / C

    print("k,epsilon,g,power_factor,delay_s,snr,capacity_bps,cap_delay_bits,cap_tau_bits,delay_over_tau")
    for k in range(1, args.decades + 1):
        epsilon = 10.0 ** (-2*k)
        r0 = rs * (1.0 + epsilon)
        if r0 == rs:
            break
        g = gravitational_redshift_factor(mass, r0)
        power_factor = g*g
        delay = coordinate_escape_delay(mass, r0, r_end)
        snr = args.far_snr * power_factor
        cap = capacity_awgn(args.bandwidth_hz, snr)
        print(f"{k},{epsilon:.6e},{g:.12e},{power_factor:.12e},{delay:.12e},{snr:.12e},{cap:.12e},{cap*delay:.12e},{cap*tau:.12e},{delay/tau:.12e}")

    print("\nAsymptotic checks:")
    print("low-SNR capacity should scale approximately as g^2")
    print("delay/tau should grow approximately as -ln(epsilon)")
    print("therefore capacity*delay should tend toward zero, not a nonzero invariant")
    print("candidate transformed quantity: ln(capacity) + delay/tau; inspect for convergence after low-SNR onset")


if __name__ == "__main__":
    main()
