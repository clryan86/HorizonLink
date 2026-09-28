"""Interactive Streamlit dashboard for HorizonLink.

Launch from the repository root after installing the dashboard extra:

    python -m pip install -e ".[dashboard]"
    horizonlink dashboard
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import streamlit as st

from horizonlink import __version__
from horizonlink.channels.gaussian import capacity_from_snr
from horizonlink.detectors.radiometer import (
    integrated_radiometer_snr,
    power_snr,
    required_integration_time,
    thermal_noise_power,
)
from horizonlink.horizons.design import (
    maximum_receiver_distance,
    required_collecting_area,
    required_transmitter_power,
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


def _format_scientific(value: float, unit: str = "") -> str:
    suffix = f" {unit}" if unit else ""
    return f"{value:.4e}{suffix}"


def _format_optional(value: float | None, unit: str = "") -> str:
    if value is None:
        return "unreachable / out of range"
    return _format_scientific(value, unit)


def _download_pair(
    scenario: dict[str, float | str | None],
    profile: pd.DataFrame,
    prefix: str,
) -> None:
    payload = {
        "schema_version": 1,
        "horizonlink_version": __version__,
        **scenario,
    }
    left, right = st.columns(2)
    left.download_button(
        "Download scenario JSON",
        data=json.dumps(payload, indent=2, sort_keys=True, allow_nan=False),
        file_name=f"{prefix}_scenario.json",
        mime="application/json",
        use_container_width=True,
    )
    right.download_button(
        "Download profile CSV",
        data=profile.to_csv(index=False),
        file_name=f"{prefix}_profile.csv",
        mime="text/csv",
        use_container_width=True,
    )


def _exterior_link_tab() -> None:
    st.subheader("Exterior-horizon communication laboratory")
    st.caption(
        "Established Schwarzschild redshift + deliberately simplified geometric link and "
        "thermal-detector models. No signaling from inside an event horizon is modeled."
    )

    left, right = st.columns(2)
    with left:
        mass_solar = st.number_input("Black-hole mass (solar masses)", 0.01, 1.0e10, 10.0)
        emitter_radius_rs = st.slider(
            "Emitter radius (Schwarzschild radii)", 1.0001, 20.0, 1.5, step=0.0001
        )
        emitted_log_hz = st.slider("log10 emitted frequency (Hz)", 3.0, 15.0, 9.0, 0.1)
        transmitter_log_w = st.slider("log10 transmitter power (W)", -6.0, 15.0, 2.0, 0.1)
        target_snr = st.number_input("Target integrated SNR", 0.01, 1.0e6, 5.0)

    with right:
        distance_log_m = st.slider("log10 receiver distance (m)", 3.0, 20.0, 9.0, 0.1)
        aperture_log_m2 = st.slider("log10 collecting area (m²)", -2.0, 8.0, 2.0, 0.1)
        bandwidth_log_hz = st.slider("log10 bandwidth (Hz)", 0.0, 10.0, 6.0, 0.1)
        system_temperature_k = st.number_input("System temperature (K)", 0.1, 1.0e6, 50.0)
        integration_time_s = st.number_input("Integration time (s)", 1.0e-6, 1.0e9, 10.0)

    emitted_hz = 10.0**emitted_log_hz
    transmitter_power_w = 10.0**transmitter_log_w
    receiver_distance_m = 10.0**distance_log_m
    aperture_area_m2 = 10.0**aperture_log_m2
    bandwidth_hz = 10.0**bandwidth_log_hz

    mass_kg = mass_solar * M_SUN
    rs = schwarzschild_radius(mass_kg)
    emitter_radius_m = emitter_radius_rs * rs
    link_fraction = horizon_link_fraction(
        mass_kg, emitter_radius_m, receiver_distance_m, aperture_area_m2
    )
    received_power_w = transmitter_power_w * link_fraction
    noise_power_w = thermal_noise_power(system_temperature_k, bandwidth_hz)
    instant_snr = power_snr(received_power_w, system_temperature_k, bandwidth_hz)
    integrated_snr = integrated_radiometer_snr(
        received_power_w,
        system_temperature_k,
        bandwidth_hz,
        integration_time_s,
    )
    capacity = capacity_from_snr(instant_snr, bandwidth_hz)
    received_hz = redshifted_frequency(mass_kg, emitter_radius_m, emitted_hz)

    try:
        required_power_w = required_transmitter_power(
            mass_kg,
            emitter_radius_m,
            receiver_distance_m,
            aperture_area_m2,
            system_temperature_k,
            bandwidth_hz,
            integration_time_s,
            target_snr,
        )
    except (ValueError, OverflowError):
        required_power_w = None

    try:
        max_distance_m = maximum_receiver_distance(
            mass_kg,
            emitter_radius_m,
            transmitter_power_w,
            aperture_area_m2,
            system_temperature_k,
            bandwidth_hz,
            integration_time_s,
            target_snr,
        )
    except (ValueError, OverflowError):
        max_distance_m = None

    try:
        required_area_m2 = required_collecting_area(
            mass_kg,
            emitter_radius_m,
            transmitter_power_w,
            receiver_distance_m,
            system_temperature_k,
            bandwidth_hz,
            integration_time_s,
            target_snr,
        )
    except (ValueError, OverflowError):
        required_area_m2 = None

    try:
        required_time_s = required_integration_time(
            received_power_w,
            system_temperature_k,
            bandwidth_hz,
            target_snr,
        )
    except (ValueError, OverflowError):
        required_time_s = None

    metric_columns = st.columns(4)
    metric_columns[0].metric("Schwarzschild radius", _format_scientific(rs, "m"))
    metric_columns[1].metric("Received frequency", _format_scientific(received_hz, "Hz"))
    metric_columns[2].metric("Received signal", _format_scientific(received_power_w, "W"))
    metric_columns[3].metric("Thermal noise", _format_scientific(noise_power_w, "W"))

    metric_columns = st.columns(4)
    metric_columns[0].metric("Power SNR", _format_scientific(instant_snr))
    metric_columns[1].metric("Integrated SNR", _format_scientific(integrated_snr))
    metric_columns[2].metric("Shannon capacity", _format_scientific(capacity, "bit/s"))
    metric_columns[3].metric("Collected fraction", _format_scientific(link_fraction))

    st.markdown("**Inverse design for the target SNR**")
    design_columns = st.columns(4)
    design_columns[0].metric(
        "Required transmitter power", _format_optional(required_power_w, "W")
    )
    design_columns[1].metric(
        "Required collecting area", _format_optional(required_area_m2, "m²")
    )
    design_columns[2].metric(
        "Required integration time", _format_optional(required_time_s, "s")
    )
    design_columns[3].metric(
        "Maximum receiver distance", _format_optional(max_distance_m, "m")
    )

    radii_rs = np.geomspace(1.0001, 50.0, 240)
    frequencies = []
    fractions = []
    for radius_ratio in radii_rs:
        radius_m = float(radius_ratio * rs)
        frequencies.append(redshifted_frequency(mass_kg, radius_m, emitted_hz) / emitted_hz)
        fractions.append(
            horizon_link_fraction(mass_kg, radius_m, receiver_distance_m, aperture_area_m2)
        )

    max_fraction = max(float(np.max(fractions)), np.finfo(float).tiny)
    profile = pd.DataFrame(
        {
            "radius / Schwarzschild radius": radii_rs,
            "received/emitted frequency": np.asarray(frequencies),
            "normalized collected power fraction": np.asarray(fractions) / max_fraction,
        }
    )
    st.markdown("**Near-horizon profile**")
    st.line_chart(
        profile,
        x="radius / Schwarzschild radius",
        y=["received/emitted frequency", "normalized collected power fraction"],
    )

    scenario = {
        "workspace": "exterior-link",
        "model_level": "analogue",
        "mass_solar": float(mass_solar),
        "emitter_radius_rs": float(emitter_radius_rs),
        "emitted_frequency_hz": emitted_hz,
        "transmitter_power_w": transmitter_power_w,
        "receiver_distance_m": receiver_distance_m,
        "aperture_area_m2": aperture_area_m2,
        "bandwidth_hz": bandwidth_hz,
        "system_temperature_k": float(system_temperature_k),
        "integration_time_s": float(integration_time_s),
        "target_integrated_snr": float(target_snr),
        "received_frequency_hz": received_hz,
        "received_signal_power_w": received_power_w,
        "instantaneous_power_snr": instant_snr,
        "integrated_radiometer_snr": integrated_snr,
        "shannon_capacity_bits_per_second": capacity,
        "required_transmitter_power_w": required_power_w,
        "required_collecting_area_m2": required_area_m2,
        "required_integration_time_s": required_time_s,
        "maximum_receiver_distance_m": max_distance_m,
    }
    _download_pair(scenario, profile, "horizonlink_exterior")


def _kerr_tab() -> None:
    st.subheader("Kerr rotation and frame dragging")
    st.caption(
        "Standard Kerr horizon/static-limit geometry and ZAMO frame-dragging angular velocity "
        "in Boyer-Lindquist coordinates."
    )

    mass_solar = st.number_input(
        "Kerr black-hole mass (solar masses)", 0.01, 1.0e10, 10.0, key="kerr_mass"
    )
    chi = st.slider("Dimensionless spin χ", -0.999, 0.999, 0.9, 0.001)
    polar_angle_deg = st.slider("Polar angle (degrees)", 0.0, 180.0, 90.0, 1.0)

    mass_kg = mass_solar * M_SUN
    polar_angle = math.radians(polar_angle_deg)
    rg = gravitational_radius(mass_kg)
    r_plus, r_minus = horizon_radii(mass_kg, chi)
    static_limit = static_limit_radius(mass_kg, chi, polar_angle)
    omega_h = horizon_angular_velocity(mass_kg, chi)

    columns = st.columns(4)
    columns[0].metric("Outer horizon", _format_scientific(r_plus, "m"))
    columns[1].metric("Inner horizon", _format_scientific(r_minus, "m"))
    columns[2].metric("Static limit", _format_scientific(static_limit, "m"))
    columns[3].metric("Horizon angular velocity", _format_scientific(omega_h, "rad/s"))

    start_rg = max(r_plus / rg, 1.0)
    radius_rg = np.geomspace(start_rg * (1.0 + 1.0e-8), 100.0, 240)
    omega = np.array(
        [
            frame_dragging_angular_velocity(mass_kg, chi, float(r * rg), polar_angle)
            for r in radius_rg
        ]
    )
    profile = pd.DataFrame(
        {
            "radius / gravitational radius": radius_rg,
            "frame dragging (rad/s)": omega,
        }
    )
    st.markdown("**Frame-dragging profile**")
    st.line_chart(profile, x="radius / gravitational radius", y="frame dragging (rad/s)")

    scenario = {
        "workspace": "kerr-rotation",
        "model_level": "established",
        "mass_solar": float(mass_solar),
        "chi": float(chi),
        "polar_angle_deg": float(polar_angle_deg),
        "outer_horizon_radius_m": r_plus,
        "inner_horizon_radius_m": r_minus,
        "static_limit_radius_m": static_limit,
        "horizon_angular_velocity_rad_s": omega_h,
    }
    _download_pair(scenario, profile, "horizonlink_kerr")


def _quantum_tab() -> None:
    st.subheader("Quantum-information laboratory")
    st.caption(
        "Three-qubit teleportation and noise experiments. These are quantum-information analogues, "
        "not a claim that entanglement permits communication out of a classical event horizon."
    )

    theta = st.slider("Input-state θ (radians)", 0.0, math.pi, math.pi / 2.0, 0.01)
    phi = st.slider("Input-state φ (radians)", -math.pi, math.pi, 0.0, 0.01)
    resource_error = st.slider("Bell-resource Pauli error probability", 0.0, 1.0, 0.0, 0.01)
    classical_error = st.slider("Classical correction-bit flip probability", 0.0, 0.5, 0.0, 0.01)
    st.caption(
        "Pauli-noise convention: identity occurs with probability 1-p and X/Y/Z each with p/3. "
        "Complete depolarization occurs at p=0.75; p=1 applies a non-identity Pauli every time."
    )

    state = qubit_state(theta, phi)
    output = teleport(
        state,
        resource_error_probability=resource_error,
        classical_bit_error_probability=classical_error,
    )
    fidelity = fidelity_pure(state, output)

    columns = st.columns(3)
    columns[0].metric("Teleportation fidelity", f"{fidelity:.6f}")
    columns[1].metric("Bob P(0)", f"{float(output[0, 0].real):.6f}")
    columns[2].metric("Bob P(1)", f"{float(output[1, 1].real):.6f}")

    error_values = np.linspace(0.0, 1.0, 101)
    fidelities = []
    for error in error_values:
        swept_output = teleport(
            state,
            resource_error_probability=float(error),
            classical_bit_error_probability=classical_error,
        )
        fidelities.append(fidelity_pure(state, swept_output))

    profile = pd.DataFrame(
        {
            "Bell-resource error probability": error_values,
            "fidelity": np.asarray(fidelities),
        }
    )
    st.markdown("**Resource-noise sweep**")
    st.line_chart(profile, x="Bell-resource error probability", y="fidelity")

    scenario = {
        "workspace": "quantum-information",
        "model_level": "analogue",
        "theta_rad": float(theta),
        "phi_rad": float(phi),
        "resource_error_probability": float(resource_error),
        "classical_bit_error_probability": float(classical_error),
        "teleportation_fidelity": fidelity,
        "bob_probability_0": float(output[0, 0].real),
        "bob_probability_1": float(output[1, 1].real),
        "pauli_noise_convention": "I:1-p; X:Y:Z=p/3; fully depolarizing at p=0.75",
    }
    _download_pair(scenario, profile, "horizonlink_quantum")


def main() -> None:
    st.set_page_config(page_title="HorizonLink Lab", page_icon="🕳️", layout="wide")
    st.title("HorizonLink Lab")
    st.write(
        "Interactive experiments for relativistic horizons, communication channels, detector "
        "sensitivity, and quantum-information toy models."
    )
    st.warning(
        "HorizonLink separates established equations from simplified and speculative models. "
        "It does not claim faster-than-light communication or signaling from inside a classical "
        "event horizon."
    )

    exterior, kerr, quantum = st.tabs(["Exterior Link", "Kerr Rotation", "Quantum Information"])
    with exterior:
        _exterior_link_tab()
    with kerr:
        _kerr_tab()
    with quantum:
        _quantum_tab()


if __name__ == "__main__":
    main()
