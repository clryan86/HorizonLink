"""Validation and deterministic replay for HorizonLink Lab scenario files.

Scenario replay deliberately recomputes outputs from saved inputs rather than
trusting previously saved numerical results. This makes exported scenarios useful
for reproducibility checks across HorizonLink versions.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

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
    gravitational_radius,
    horizon_angular_velocity,
    horizon_radii,
    static_limit_radius,
)
from horizonlink.horizons.link_budget import horizon_link_fraction, redshifted_frequency
from horizonlink.horizons.schwarzschild import M_SUN, schwarzschild_radius
from horizonlink.protocols.teleportation import teleport
from horizonlink.quantum.states import fidelity_pure, qubit_state

SCENARIO_SCHEMA_VERSION = 1
SUPPORTED_WORKSPACES = frozenset({"exterior-link", "kerr-rotation", "quantum-information"})


class ScenarioError(ValueError):
    """Raised when an exported HorizonLink scenario cannot be replayed safely."""


def _finite_number(payload: Mapping[str, Any], key: str) -> float:
    if key not in payload:
        raise ScenarioError(f"scenario is missing required field: {key}")
    value = payload[key]
    if isinstance(value, bool):
        raise ScenarioError(f"scenario field {key} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ScenarioError(f"scenario field {key} must be a finite number") from exc
    if not math.isfinite(number):
        raise ScenarioError(f"scenario field {key} must be finite")
    return number


def validate_scenario(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the common HorizonLink scenario envelope and return a plain dict."""
    if not isinstance(payload, Mapping):
        raise ScenarioError("scenario must be a JSON object")
    scenario = dict(payload)

    schema_version = scenario.get("schema_version")
    if schema_version != SCENARIO_SCHEMA_VERSION:
        raise ScenarioError(
            f"unsupported scenario schema_version {schema_version!r}; "
            f"expected {SCENARIO_SCHEMA_VERSION}"
        )

    workspace = scenario.get("workspace")
    if workspace not in SUPPORTED_WORKSPACES:
        raise ScenarioError(f"unsupported scenario workspace: {workspace!r}")

    version = scenario.get("horizonlink_version")
    if not isinstance(version, str) or not version.strip():
        raise ScenarioError("scenario is missing a valid horizonlink_version")

    model_level = scenario.get("model_level")
    if model_level not in {"established", "analogue", "speculative-toy"}:
        raise ScenarioError("scenario has an invalid model_level")

    return scenario


def _optional_inverse(function, *args) -> float | None:
    try:
        value = float(function(*args))
    except (ValueError, OverflowError):
        return None
    if not math.isfinite(value):
        return None
    return value


def _replay_exterior(scenario: Mapping[str, Any]) -> dict[str, Any]:
    mass_solar = _finite_number(scenario, "mass_solar")
    emitter_radius_rs = _finite_number(scenario, "emitter_radius_rs")
    emitted_hz = _finite_number(scenario, "emitted_frequency_hz")
    transmitter_power = _finite_number(scenario, "transmitter_power_w")
    receiver_distance = _finite_number(scenario, "receiver_distance_m")
    aperture_area = _finite_number(scenario, "aperture_area_m2")
    bandwidth = _finite_number(scenario, "bandwidth_hz")
    temperature = _finite_number(scenario, "system_temperature_k")
    integration_time = _finite_number(scenario, "integration_time_s")
    target_snr = _finite_number(scenario, "target_integrated_snr")

    if transmitter_power <= 0.0:
        raise ScenarioError("transmitter_power_w must be positive for scenario replay")

    mass_kg = mass_solar * M_SUN
    rs = schwarzschild_radius(mass_kg)
    emitter_radius = emitter_radius_rs * rs
    fraction = horizon_link_fraction(
        mass_kg,
        emitter_radius,
        receiver_distance,
        aperture_area,
    )
    received_power = transmitter_power * fraction
    instantaneous_snr = power_snr(received_power, temperature, bandwidth)
    integrated_snr = integrated_radiometer_snr(
        received_power,
        temperature,
        bandwidth,
        integration_time,
    )

    required_power = _optional_inverse(
        required_transmitter_power,
        mass_kg,
        emitter_radius,
        receiver_distance,
        aperture_area,
        temperature,
        bandwidth,
        integration_time,
        target_snr,
    )
    required_area = _optional_inverse(
        required_collecting_area,
        mass_kg,
        emitter_radius,
        transmitter_power,
        receiver_distance,
        temperature,
        bandwidth,
        integration_time,
        target_snr,
    )
    required_time = _optional_inverse(
        required_integration_time,
        received_power,
        temperature,
        bandwidth,
        target_snr,
    )
    max_distance = _optional_inverse(
        maximum_receiver_distance,
        mass_kg,
        emitter_radius,
        transmitter_power,
        aperture_area,
        temperature,
        bandwidth,
        integration_time,
        target_snr,
    )

    return {
        "workspace": "exterior-link",
        "model_level": "analogue",
        "schwarzschild_radius_m": rs,
        "received_frequency_hz": redshifted_frequency(mass_kg, emitter_radius, emitted_hz),
        "received_power_fraction": fraction,
        "received_signal_power_w": received_power,
        "thermal_noise_power_w": thermal_noise_power(temperature, bandwidth),
        "instantaneous_power_snr": instantaneous_snr,
        "integrated_radiometer_snr": integrated_snr,
        "shannon_capacity_bits_per_second": capacity_from_snr(instantaneous_snr, bandwidth),
        "required_transmitter_power_w": required_power,
        "required_collecting_area_m2": required_area,
        "required_integration_time_s": required_time,
        "maximum_receiver_distance_m": max_distance,
    }


def _replay_kerr(scenario: Mapping[str, Any]) -> dict[str, Any]:
    mass_solar = _finite_number(scenario, "mass_solar")
    chi = _finite_number(scenario, "chi")
    polar_angle_deg = _finite_number(scenario, "polar_angle_deg")

    mass_kg = mass_solar * M_SUN
    polar_angle = math.radians(polar_angle_deg)
    rg = gravitational_radius(mass_kg)
    r_plus, r_minus = horizon_radii(mass_kg, chi)
    return {
        "workspace": "kerr-rotation",
        "model_level": "established",
        "gravitational_radius_m": rg,
        "outer_horizon_radius_m": r_plus,
        "inner_horizon_radius_m": r_minus,
        "static_limit_radius_m": static_limit_radius(mass_kg, chi, polar_angle),
        "horizon_angular_velocity_rad_s": horizon_angular_velocity(mass_kg, chi),
    }


def _replay_quantum(scenario: Mapping[str, Any]) -> dict[str, Any]:
    theta = _finite_number(scenario, "theta_rad")
    phi = _finite_number(scenario, "phi_rad")
    resource_error = _finite_number(scenario, "resource_error_probability")
    classical_error = _finite_number(scenario, "classical_bit_error_probability")

    state = qubit_state(theta, phi)
    output = teleport(
        state,
        resource_error_probability=resource_error,
        classical_bit_error_probability=classical_error,
    )
    return {
        "workspace": "quantum-information",
        "model_level": "analogue",
        "teleportation_fidelity": fidelity_pure(state, output),
        "bob_probability_0": float(output[0, 0].real),
        "bob_probability_1": float(output[1, 1].real),
        "bob_coherence_magnitude": float(abs(output[0, 1])),
    }


def replay_scenario(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and recompute a saved HorizonLink Lab scenario from its inputs."""
    scenario = validate_scenario(payload)
    workspace = scenario["workspace"]
    if workspace == "exterior-link":
        return _replay_exterior(scenario)
    if workspace == "kerr-rotation":
        return _replay_kerr(scenario)
    return _replay_quantum(scenario)


def comparison_rows(
    scenario: Mapping[str, Any],
    replayed: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Return comparable saved/recomputed numeric fields for UI or CLI display."""
    rows: list[dict[str, Any]] = []
    for key in sorted(set(scenario).intersection(replayed)):
        saved = scenario[key]
        recomputed = replayed[key]
        if isinstance(saved, bool) or isinstance(recomputed, bool):
            continue
        if not isinstance(saved, (int, float)) or not isinstance(recomputed, (int, float)):
            continue
        saved_value = float(saved)
        recomputed_value = float(recomputed)
        if not (math.isfinite(saved_value) and math.isfinite(recomputed_value)):
            continue
        absolute_difference = abs(recomputed_value - saved_value)
        scale = max(abs(saved_value), abs(recomputed_value), 1.0e-300)
        rows.append(
            {
                "field": key,
                "saved": saved_value,
                "recomputed": recomputed_value,
                "absolute_difference": absolute_difference,
                "relative_difference": absolute_difference / scale,
            }
        )
    return rows
