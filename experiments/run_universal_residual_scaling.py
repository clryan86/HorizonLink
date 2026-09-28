"""Test the universal first-order residual of the exterior Schwarzschild toy channel.

Let x=r/rs=1+epsilon and R=r_receiver/rs.  For a radial outgoing null ray,

    t/(rs/c) = (R-x) + ln((R-1)/(x-1)).

The gravitational power factor is g^2=(x-1)/x. In the low-SNR AWGN limit,
capacity is proportional to g^2. Therefore

    Q = ln(C) + t/(rs/c)

has a finite horizon limit. More strongly, after subtracting that limit, all
mass, bandwidth, reference-SNR, and receiver-radius constants cancel:

    Q(epsilon)-Q(0) = -ln(1+epsilon)-epsilon
                         = -2 epsilon + epsilon^2/2 + O(epsilon^3).

Thus the normalized residual [Q(epsilon)-Q(0)]/epsilon -> -2.

This is a derived scaling law inside the present idealized model, not evidence
of new fundamental physics or communication through an event horizon. The
purpose of this script is to make the prediction explicit and falsifiable when
more realistic propagation/noise models are added.
"""
from __future__ import annotations

import argparse
import math


def exact_residual(epsilon: float) -> float:
    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    return -math.log1p(epsilon) - epsilon


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--min-power", type=int, default=1)
    p.add_argument("--max-power", type=int, default=14)
    args = p.parse_args()

    print("epsilon,residual,residual_over_epsilon,error_from_minus_2")
    for power in range(args.min_power, args.max_power + 1):
        epsilon = 10.0 ** (-power)
        residual = exact_residual(epsilon)
        ratio = residual / epsilon
        print(f"{epsilon:.12e},{residual:.12e},{ratio:.12e},{ratio + 2.0:.12e}")

    print("\nPrediction: residual/epsilon -> -2 as epsilon -> 0+.")
    print("If a richer channel model does not approach -2, it identifies which added physics breaks the toy universality.")


if __name__ == "__main__":
    main()
