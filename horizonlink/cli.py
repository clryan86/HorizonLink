"""Command-line interface for HorizonLink."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from horizonlink.channels.binary_symmetric import capacity_bits_per_use
from horizonlink.channels.gaussian import capacity_from_snr, snr_db_to_linear
from horizonlink.detectors.radiometer import (
    integrated_radiometer_snr,
    power_snr,
    thermal_noise_power,
)
from horizonlink.horizons.kerr import (
    frame_dragging_angular_velocity,
    gravitational_radius,
    horizon_angular_velocity,
    horizon_radii,
    static_limit_radius,
)
from horizonlink.horizons.link_budget import horizon_link_fraction, redshifted_frequency
from horizonlink.horizons.schwarzschild import M_SUN, schwarzschild_radius
from horizonlink.protocols.teleportation import teleport
from horizonlink.quantum.states import fidelity_pure, qubit_state
from horizonlink.simulation.monte_carlo import run_bsc_trials


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="horizonlink",
        description="Reproducible toy-model experiments for horizon information channels.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("dashboard", help="Launch the interactive HorizonLink Lab browser dashboard")

    radius = sub.add_parser("radius", help="Compute a Schwarzschild radius")
    radius.add_argument("mass_solar", type=float, help="Black-hole mass in solar masses")

    kerr = sub.add_parser("kerr", help="Compute Kerr horizon and ergosphere quantities")
    kerr.add_argument("mass_solar", type=float)
    kerr.add_argument("chi", type=float, help="Dimensionless spin cJ/(GM^2), with |chi| <= 1")
    kerr.add_argument(
        "--polar-angle",
        type=float,
        default=1.5707963267948966,
        help="Boyer-Lindquist polar angle in radians for static-limit radius",
    )
    kerr.add_argument(
        "--frame-radius-rg",
        type=float,
        default=10.0,
        help="Radius in gravitational radii GM/c^2 for frame-dragging output",
    )

    bsc = sub.add_parser("bsc-capacity", help="Binary symmetric channel capacity")
    bsc.add_argument("flip_probability", type=float)

    awgn = sub.add_parser("awgn-capacity", help="Shannon-Hartley AWGN capacity")
    awgn.add_argument("snr_db", type=float)
    awgn.add_argument("bandwidth_hz", type=float)

    mc = sub.add_parser("monte-carlo", help="Run reproducible BSC Monte Carlo trials")
    mc.add_argument("flip_probability", type=float)
    mc.add_argument("--trials", type=int, default=100)
    mc.add_argument("--bits", type=int, default=10_000)
    mc.add_argument("--seed", type=int, default=0)

    link = sub.add_parser("link-budget", help="Estimate a toy exterior-horizon link fraction")
    link.add_argument("mass_solar", type=float)
    link.add_argument("emitter_radius_rs", type=float, help="Emitter radius in Schwarzschild radii")
    link.add_argument("receiver_distance_m", type=float)
    link.add_argument("emitted_hz", type=float)
    link.add_argument("--aperture-area-m2", type=float, default=1.0)

    detect = sub.add_parser(
        "link-detect",
        help="Combine the exterior link model with idealized thermal detector sensitivity",
    )
    detect.add_argument("mass_solar", type=float)
    detect.add_argument("emitter_radius_rs", type=float)
    detect.add_argument("receiver_distance_m", type=float)
    detect.add_argument("emitted_hz", type=float)
    detect.add_argument("transmitter_power_w", type=float)
    detect.add_argument("system_temperature_k", type=float)
    detect.add_argument("bandwidth_hz", type=float)
    detect.add_argument("integration_time_s", type=float)
    detect.add_argument("--aperture-area-m2", type=float, default=1.0)

    tp = sub.add_parser("teleport", help="Run the three-qubit teleportation toy model")
    tp.add_argument("theta", type=float, help="Input-state Bloch polar angle in radians")
    tp.add_argument("--phi", type=float, default=0.0, help="Bloch azimuth angle in radians")
    tp.add_argument(
        "--resource-error",
        type=float,
        default=0.0,
        help="Pauli error probability on Bob's half of the Bell pair",
    )
    tp.add_argument(
        "--classical-bit-error",
        type=float,
        default=0.0,
        help="Independent flip probability for each of Alice's two classical correction bits",
    )

    return parser


def _launch_dashboard(parser: argparse.ArgumentParser) -> int:
    if importlib.util.find_spec("streamlit") is None:
        parser.error('Dashboard dependencies are not installed. Run: pip install -e ".[dashboard]"')
    dashboard_path = Path(__file__).with_name("dashboard.py")
    result = subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(dashboard_path)],
        check=False,
    )
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.command == "dashboard":
        return _launch_dashboard(parser)

    if args.command == "radius":
        mass_kg = args.mass_solar * M_SUN
        payload = {
            "mass_solar": args.mass_solar,
            "schwarzschild_radius_m": schwarzschild_radius(mass_kg),
        }
    elif args.command == "kerr":
        mass_kg = args.mass_solar * M_SUN
        r_plus, r_minus = horizon_radii(mass_kg, args.chi)
        rg = gravitational_radius(mass_kg)
        frame_radius = args.frame_radius_rg * rg
        payload = {
            "mass_solar": args.mass_solar,
            "chi": args.chi,
            "outer_horizon_radius_m": r_plus,
            "inner_horizon_radius_m": r_minus,
            "static_limit_radius_m": static_limit_radius(
                mass_kg, args.chi, args.polar_angle
            ),
            "horizon_angular_velocity_rad_s": horizon_angular_velocity(mass_kg, args.chi),
            "frame_radius_rg": args.frame_radius_rg,
            "frame_dragging_angular_velocity_rad_s": frame_dragging_angular_velocity(
                mass_kg, args.chi, frame_radius, args.polar_angle
            ),
        }
    elif args.command == "bsc-capacity":
        payload = {
            "flip_probability": args.flip_probability,
            "capacity_bits_per_use": capacity_bits_per_use(args.flip_probability),
        }
    elif args.command == "awgn-capacity":
        snr_linear = snr_db_to_linear(args.snr_db)
        payload = {
            "snr_db": args.snr_db,
            "bandwidth_hz": args.bandwidth_hz,
            "capacity_bits_per_second": capacity_from_snr(snr_linear, args.bandwidth_hz),
        }
    elif args.command == "monte-carlo":
        payload = run_bsc_trials(
            args.flip_probability,
            trials=args.trials,
            bits_per_trial=args.bits,
            seed=args.seed,
        ).as_dict()
    elif args.command == "teleport":
        state = qubit_state(args.theta, args.phi)
        output = teleport(
            state,
            resource_error_probability=args.resource_error,
            classical_bit_error_probability=args.classical_bit_error,
        )
        payload = {
            "theta": args.theta,
            "phi": args.phi,
            "resource_error_probability": args.resource_error,
            "classical_bit_error_probability": args.classical_bit_error,
            "fidelity": fidelity_pure(state, output),
            "bob_probability_0": float(output[0, 0].real),
            "bob_probability_1": float(output[1, 1].real),
            "bob_coherence_magnitude": float(abs(output[0, 1])),
        }
    elif args.command == "link-detect":
        if args.transmitter_power_w < 0.0:
            raise ValueError("transmitter_power_w cannot be negative")
        mass_kg = args.mass_solar * M_SUN
        rs = schwarzschild_radius(mass_kg)
        emitter_radius = args.emitter_radius_rs * rs
        link_fraction = horizon_link_fraction(
            mass_kg,
            emitter_radius,
            args.receiver_distance_m,
            args.aperture_area_m2,
        )
        received_power = args.transmitter_power_w * link_fraction
        instantaneous_snr = power_snr(
            received_power,
            args.system_temperature_k,
            args.bandwidth_hz,
        )
        integrated_snr = integrated_radiometer_snr(
            received_power,
            args.system_temperature_k,
            args.bandwidth_hz,
            args.integration_time_s,
        )
        payload = {
            "mass_solar": args.mass_solar,
            "emitter_radius_rs": args.emitter_radius_rs,
            "redshifted_frequency_hz": redshifted_frequency(
                mass_kg, emitter_radius, args.emitted_hz
            ),
            "received_power_fraction": link_fraction,
            "received_signal_power_w": received_power,
            "thermal_noise_power_w": thermal_noise_power(
                args.system_temperature_k, args.bandwidth_hz
            ),
            "instantaneous_power_snr": instantaneous_snr,
            "integrated_radiometer_snr": integrated_snr,
            "shannon_capacity_bits_per_second": capacity_from_snr(
                instantaneous_snr, args.bandwidth_hz
            ),
        }
    else:
        mass_kg = args.mass_solar * M_SUN
        rs = schwarzschild_radius(mass_kg)
        emitter_radius = args.emitter_radius_rs * rs
        payload = {
            "mass_solar": args.mass_solar,
            "emitter_radius_rs": args.emitter_radius_rs,
            "redshifted_frequency_hz": redshifted_frequency(
                mass_kg, emitter_radius, args.emitted_hz
            ),
            "received_power_fraction": horizon_link_fraction(
                mass_kg,
                emitter_radius,
                args.receiver_distance_m,
                args.aperture_area_m2,
            ),
        }

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
