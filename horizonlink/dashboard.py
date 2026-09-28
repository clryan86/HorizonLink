"""Interactive Streamlit dashboard for HorizonLink.

Launch from the repository root after installing the dashboard extra:

    python -m pip install -e ".[dashboard]"
    python -m streamlit run horizonlink/dashboard.py
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import streamlit as st

from horizonlink.channels.gaussian import capacity_from_snr
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


def _format_scientific(value: float, unit: str = "") -> str:
    suffix = f" {unit}" if unit else ""
    return f"{value:.4e}{suffix}"


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
