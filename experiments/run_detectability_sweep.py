"""Sweep exterior emitter radius and quantify idealized link detectability.

Example:
    python experiments/run_detectability_sweep.py --mass-solar 10 --output results/detectability.csv

The calculation combines the Schwarzschild exterior link model with the simple
thermal radiometer model. It is a transparent baseline, not a full telescope or
relativistic radiative-transfer simulation.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from horizonlink.channels.gaussian import capacity_from_snr
from horizonlink.detectors.radiometer import (
    integrated_radiometer_snr,
    power_snr,
    thermal_noise_power,
)
from horizonlink.horizons.link_budget import horizon_link_fraction, redshifted_frequency
from horizonlink.horizons.schwarzschild import M_SUN, schwarzschild_radius


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mass-solar", type=float, default=10.0)
    parser.add_argument("--radius-min-rs", type=float, default=1.0001)
    parser.add_argument("--radius-max-rs", type=float, default=20.0)
    parser.add_argument("--points", type=int, default=240)
    parser.add_argument("--emitted-hz", type=float, default=1.0e9)
    parser.add_argument("--transmitter-power-w", type=float, default=100.0)
    parser.add_argument("--receiver-distance-m", type=float, default=1.0e9)
    parser.add_argument("--aperture-area-m2", type=float, default=100.0)
    parser.add_argument("--system-temperature-k", type=float, default=50.0)
    parser.add_argument("--bandwidth-hz", type=float, default=1.0e6)
    parser.add_argument("--integration-time-s", type=float, default=10.0)
    parser.add_argument("--output", type=Path, default=Path("results/detectability_sweep.csv"))
    args = parser.parse_args()

    if args.mass_solar <= 0.0:
        raise ValueError("--mass-solar must be positive")
    if args.radius_min_rs <= 1.0:
        raise ValueError("--radius-min-rs must be outside the event horizon (> 1)")
    if args.radius_max_rs <= args.radius_min_rs:
        raise ValueError("--radius-max-rs must exceed --radius-min-rs")
    if args.points < 2:
        raise ValueError("--points must be at least 2")
    if args.transmitter_power_w < 0.0:
        raise ValueError("--transmitter-power-w cannot be negative")

    mass_kg = args.mass_solar * M_SUN
    rs = schwarzschild_radius(mass_kg)
    radius_ratios = np.geomspace(args.radius_min_rs, args.radius_max_rs, args.points)
    noise_power = thermal_noise_power(args.system_temperature_k, args.bandwidth_hz)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "radius_rs",
                "radius_m",
                "received_frequency_hz",
                "received_power_fraction",
                "received_signal_power_w",
                "thermal_noise_power_w",
                "instantaneous_power_snr",
                "integrated_radiometer_snr",
                "shannon_capacity_bits_per_second",
            ],
        )
        writer.writeheader()

        for radius_ratio in radius_ratios:
            radius_m = float(radius_ratio * rs)
            link_fraction = horizon_link_fraction(
                mass_kg,
                radius_m,
                args.receiver_distance_m,
                args.aperture_area_m2,
            )
            signal_power = args.transmitter_power_w * link_fraction
            instant_snr = power_snr(
                signal_power,
                args.system_temperature_k,
                args.bandwidth_hz,
            )
            writer.writerow(
                {
                    "radius_rs": float(radius_ratio),
                    "radius_m": radius_m,
                    "received_frequency_hz": redshifted_frequency(
                        mass_kg, radius_m, args.emitted_hz
                    ),
                    "received_power_fraction": link_fraction,
                    "received_signal_power_w": signal_power,
                    "thermal_noise_power_w": noise_power,
                    "instantaneous_power_snr": instant_snr,
                    "integrated_radiometer_snr": integrated_radiometer_snr(
                        signal_power,
                        args.system_temperature_k,
                        args.bandwidth_hz,
                        args.integration_time_s,
                    ),
                    "shannon_capacity_bits_per_second": capacity_from_snr(
                        instant_snr, args.bandwidth_hz
                    ),
                }
            )

    print(f"wrote {args.points} rows to {args.output}")


if __name__ == "__main__":
    main()
