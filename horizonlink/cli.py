"""Command-line interface for HorizonLink."""

from __future__ import annotations

import argparse
import json

from horizonlink.channels.binary_symmetric import capacity_bits_per_use
from horizonlink.channels.gaussian import capacity_from_snr, snr_db_to_linear
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

    radius = sub.add_parser("radius", help="Compute a Schwarzschild radius")
    radius.add_argument("mass_solar", type=float, help="Black-hole mass in solar masses")

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

    tp = sub.add_parser("teleport", help="Run the three-qubit teleportation toy model")
    tp.add_argument("theta", type=float, help="Input-state Bloch polar angle in radians")
    tp.add_argument("--phi", type=float, default=0.0, help="Bloch azimuth angle in radians")
    tp.add_argument(
        "--resource-error",
        type=float,
        default=0.0,
        help="Pauli error probability on Bob's half of the Bell pair",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "radius":
        mass_kg = args.mass_solar * M_SUN
        payload = {
            "mass_solar": args.mass_solar,
            "schwarzschild_radius_m": schwarzschild_radius(mass_kg),
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
        output = teleport(state, resource_error_probability=args.resource_error)
        payload = {
            "theta": args.theta,
            "phi": args.phi,
            "resource_error_probability": args.resource_error,
            "fidelity": fidelity_pure(state, output),
            "bob_probability_0": float(output[0, 0].real),
            "bob_probability_1": float(output[1, 1].real),
            "bob_coherence_magnitude": float(abs(output[0, 1])),
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
