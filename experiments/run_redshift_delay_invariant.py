"""Probe the near-horizon redshift/delay scaling in Schwarzschild spacetime.

For an outgoing radial signal emitted at r0 and received at a fixed r1, the
exact Schwarzschild formulas imply that, as r0 -> rs+, the received frequency
factor g ~ sqrt((r0-rs)/rs), while the coordinate escape time grows as
-(rs/c) ln(r0-rs). Therefore successive decades of frequency suppression
should cost an asymptotically constant additional delay:

    Delta t per decade(g) -> 2 * rs/c * ln(10).

This is a standard-GR scaling test, not evidence for superluminal signaling or
communication from inside an event horizon.
"""

from __future__ import annotations

import argparse
import math

from horizonlink.horizons.schwarzschild import (
    C,
    M_SUN,
    coordinate_escape_delay,
    gravitational_redshift_factor,
    schwarzschild_radius,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mass-solar", type=float, default=30.0)
    parser.add_argument("--receiver-rs", type=float, default=100.0)
    parser.add_argument("--decades", type=int, default=12)
    args = parser.parse_args()

    mass = args.mass_solar * M_SUN
    rs = schwarzschild_radius(mass)
    r_end = args.receiver_rs * rs
    predicted = 2.0 * rs / C * math.log(10.0)

    print(f"mass = {args.mass_solar:g} M_sun")
    print(f"rs = {rs:.12g} m")
    print(f"near-horizon predicted delay per redshift decade = {predicted:.12g} s")
    print("decade,epsilon,g,delay_s,increment_s,increment/predicted")

    previous_delay = None
    # epsilon=(r-rs)/rs. Reducing epsilon by 100 reduces g by ~10, i.e. one
    # decade in received/emitted frequency ratio near the horizon.
    for k in range(1, args.decades + 1):
        epsilon = 10.0 ** (-2 * k)
        r_start = rs * (1.0 + epsilon)
        if r_start == rs:
            print(f"{k},{epsilon:.3e},float64-resolution-limit")
            break
        g = gravitational_redshift_factor(mass, r_start)
        delay = coordinate_escape_delay(mass, r_start, r_end)
        if previous_delay is None:
            increment = float("nan")
            ratio = float("nan")
        else:
            increment = delay - previous_delay
            ratio = increment / predicted
        print(f"{k},{epsilon:.3e},{g:.12g},{delay:.12g},{increment:.12g},{ratio:.12g}")
        previous_delay = delay


if __name__ == "__main__":
    main()
