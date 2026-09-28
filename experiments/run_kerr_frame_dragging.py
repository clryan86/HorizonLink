"""Generate a Kerr frame-dragging profile outside the outer horizon.

The output is a CSV table of Boyer-Lindquist radius and ZAMO angular velocity.
This is a standard Kerr exterior calculation, not a communication model.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from horizonlink.horizons.kerr import (
    frame_dragging_angular_velocity,
    gravitational_radius,
    outer_horizon_radius,
)
from horizonlink.horizons.schwarzschild import M_SUN
from horizonlink.provenance import experiment_metadata, write_csv_with_metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mass-solar", type=float, default=10.0)
    parser.add_argument("--spin", type=float, default=0.9, help="Dimensionless Kerr spin chi")
    parser.add_argument("--points", type=int, default=200)
    parser.add_argument("--max-radius-rg", type=float, default=100.0)
    parser.add_argument("--output", type=Path, default=Path("kerr_frame_dragging.csv"))
    args = parser.parse_args()

    if args.points < 2:
        raise ValueError("--points must be at least 2")

    mass_kg = args.mass_solar * M_SUN
    rg = gravitational_radius(mass_kg)
    r_plus = outer_horizon_radius(mass_kg, args.spin)
    max_radius = args.max_radius_rg * rg
    if max_radius <= r_plus:
        raise ValueError("--max-radius-rg must place the outer sample beyond the horizon")

    radii = np.geomspace(r_plus * (1.0 + 1.0e-9), max_radius, args.points)
    rows = []
    for radius_m in radii:
        radius = float(radius_m)
        rows.append(
            {
                "radius_m": radius,
                "radius_rg": radius / rg,
                "frame_dragging_rad_s": frame_dragging_angular_velocity(
                    mass_kg, args.spin, radius
                ),
            }
        )

    metadata = experiment_metadata(
        experiment="kerr-frame-dragging-profile",
        model_level="established",
        inputs={
            "mass_solar": args.mass_solar,
            "spin_chi": args.spin,
            "points": args.points,
            "max_radius_rg": args.max_radius_rg,
            "sample_start_radius_m": float(radii[0]),
            "outer_horizon_radius_m": r_plus,
        },
    )
    data_path, sidecar = write_csv_with_metadata(
        args.output,
        fieldnames=["radius_m", "radius_rg", "frame_dragging_rad_s"],
        rows=rows,
        metadata=metadata,
    )

    print(f"wrote {len(rows)} rows to {data_path}")
    print(f"wrote metadata to {sidecar}")


if __name__ == "__main__":
    main()
