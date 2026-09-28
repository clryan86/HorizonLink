"""Generate a CSV profile of redshift and toy link strength versus radius.

Run from the repository root:
    python experiments/run_horizon_profile.py --mass-solar 10 --output horizon_profile.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from horizonlink.horizons.link_budget import horizon_link_fraction, redshifted_frequency
from horizonlink.horizons.schwarzschild import M_SUN, schwarzschild_radius
from horizonlink.provenance import experiment_metadata, write_csv_with_metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mass-solar", type=float, default=10.0)
    parser.add_argument("--emitted-hz", type=float, default=1.0e9)
    parser.add_argument("--receiver-distance-m", type=float, default=1.0e9)
    parser.add_argument("--aperture-area-m2", type=float, default=100.0)
    parser.add_argument("--points", type=int, default=200)
    parser.add_argument("--output", type=Path, default=Path("horizon_profile.csv"))
    args = parser.parse_args()

    if args.points < 2:
        raise ValueError("--points must be at least 2")

    mass_kg = args.mass_solar * M_SUN
    rs = schwarzschild_radius(mass_kg)
    radii_rs = np.geomspace(1.0001, 100.0, args.points)

    rows = []
    for radius_ratio in radii_rs:
        radius_m = float(radius_ratio * rs)
        rows.append(
            {
                "radius_rs": float(radius_ratio),
                "radius_m": radius_m,
                "received_frequency_hz": redshifted_frequency(
                    mass_kg, radius_m, args.emitted_hz
                ),
                "received_power_fraction": horizon_link_fraction(
                    mass_kg,
                    radius_m,
                    args.receiver_distance_m,
                    args.aperture_area_m2,
                ),
            }
        )

    metadata = experiment_metadata(
        experiment="schwarzschild-horizon-profile",
        model_level="analogue",
        inputs={
            "mass_solar": args.mass_solar,
            "emitted_hz": args.emitted_hz,
            "receiver_distance_m": args.receiver_distance_m,
            "aperture_area_m2": args.aperture_area_m2,
            "points": args.points,
            "radius_min_rs": 1.0001,
            "radius_max_rs": 100.0,
        },
    )
    data_path, sidecar = write_csv_with_metadata(
        args.output,
        fieldnames=[
            "radius_rs",
            "radius_m",
            "received_frequency_hz",
            "received_power_fraction",
        ],
        rows=rows,
        metadata=metadata,
    )

    print(f"wrote {len(rows)} rows to {data_path}")
    print(f"wrote metadata to {sidecar}")


if __name__ == "__main__":
    main()
