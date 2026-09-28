"""Sweep exterior emitter radius and quantify idealized link detectability.

Example:
    python experiments/run_detectability_sweep.py --mass-solar 10 --output results/detectability.csv

The calculation combines the Schwarzschild exterior link model with the simple
thermal radiometer model. It is a transparent baseline, not a full telescope or
relativistic radiative-transfer simulation.
"""

from __future__ import annotations

import argparse
import math
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
from horizonlink.provenance import experiment_metadata, write_csv_with_metadata

FIELDS = [
    "radius_rs",
    "radius_m",
    "received_frequency_hz",
    "received_power_fraction",
    "received_signal_power_w",
    "thermal_noise_power_w",
    "instantaneous_power_snr",
    "integrated_radiometer_snr",
    "shannon_capacity_bits_per_second",
]


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def build_rows(args: argparse.Namespace) -> list[dict[str, float]]:
    """Validate a configuration and calculate all rows before any file is replaced."""
    mass_solar = _finite("--mass-solar", args.mass_solar)
    radius_min_rs = _finite("--radius-min-rs", args.radius_min_rs)
    radius_max_rs = _finite("--radius-max-rs", args.radius_max_rs)
    emitted_hz = _finite("--emitted-hz", args.emitted_hz)
    transmitter_power_w = _finite("--transmitter-power-w", args.transmitter_power_w)
    receiver_distance_m = _finite("--receiver-distance-m", args.receiver_distance_m)
    aperture_area_m2 = _finite("--aperture-area-m2", args.aperture_area_m2)
    system_temperature_k = _finite("--system-temperature-k", args.system_temperature_k)
    bandwidth_hz = _finite("--bandwidth-hz", args.bandwidth_hz)
    integration_time_s = _finite("--integration-time-s", args.integration_time_s)

    if mass_solar <= 0.0:
        raise ValueError("--mass-solar must be positive")
    if radius_min_rs <= 1.0:
        raise ValueError("--radius-min-rs must be outside the event horizon (> 1)")
    if radius_max_rs <= radius_min_rs:
        raise ValueError("--radius-max-rs must exceed --radius-min-rs")
    if args.points < 2:
        raise ValueError("--points must be at least 2")
    if transmitter_power_w < 0.0:
        raise ValueError("--transmitter-power-w cannot be negative")

    mass_kg = mass_solar * M_SUN
    rs = schwarzschild_radius(mass_kg)
    radius_ratios = np.geomspace(radius_min_rs, radius_max_rs, args.points)
    noise_power = thermal_noise_power(system_temperature_k, bandwidth_hz)

    rows: list[dict[str, float]] = []
    for radius_ratio in radius_ratios:
        radius_m = float(radius_ratio * rs)
        link_fraction = horizon_link_fraction(
            mass_kg,
            radius_m,
            receiver_distance_m,
            aperture_area_m2,
        )
        signal_power = transmitter_power_w * link_fraction
        instant_snr = power_snr(signal_power, system_temperature_k, bandwidth_hz)
        rows.append(
            {
                "radius_rs": float(radius_ratio),
                "radius_m": radius_m,
                "received_frequency_hz": redshifted_frequency(mass_kg, radius_m, emitted_hz),
                "received_power_fraction": link_fraction,
                "received_signal_power_w": signal_power,
                "thermal_noise_power_w": noise_power,
                "instantaneous_power_snr": instant_snr,
                "integrated_radiometer_snr": integrated_radiometer_snr(
                    signal_power,
                    system_temperature_k,
                    bandwidth_hz,
                    integration_time_s,
                ),
                "shannon_capacity_bits_per_second": capacity_from_snr(
                    instant_snr, bandwidth_hz
                ),
            }
        )
    return rows


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

    rows = build_rows(args)
    metadata = experiment_metadata(
        experiment="detectability_sweep",
        model_level="analogue",
        inputs={
            "mass_solar": args.mass_solar,
            "radius_min_rs": args.radius_min_rs,
            "radius_max_rs": args.radius_max_rs,
            "points": args.points,
            "emitted_hz": args.emitted_hz,
            "transmitter_power_w": args.transmitter_power_w,
            "receiver_distance_m": args.receiver_distance_m,
            "aperture_area_m2": args.aperture_area_m2,
            "system_temperature_k": args.system_temperature_k,
            "bandwidth_hz": args.bandwidth_hz,
            "integration_time_s": args.integration_time_s,
        },
    )
    metadata["model_id"] = "schwarzschild-distant-link+radiometer-v1"
    metadata["units"] = {
        "radius_m": "m",
        "received_frequency_hz": "Hz",
        "received_signal_power_w": "W",
        "thermal_noise_power_w": "W",
        "shannon_capacity_bits_per_second": "bit/s",
    }
    data_path, sidecar_path = write_csv_with_metadata(
        args.output,
        fieldnames=FIELDS,
        rows=rows,
        metadata=metadata,
    )
    print(f"wrote {len(rows)} rows to {data_path}")
    print(f"wrote provenance to {sidecar_path}")


if __name__ == "__main__":
    main()
