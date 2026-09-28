import pytest

from horizonlink.scenarios import ScenarioError, comparison_rows, replay_scenario, validate_scenario


def _quantum_scenario(**overrides):
    payload = {
        "schema_version": 1,
        "horizonlink_version": "0.4.0",
        "workspace": "quantum-information",
        "model_level": "analogue",
        "theta_rad": 1.17,
        "phi_rad": 0.73,
        "resource_error_probability": 0.75,
        "classical_bit_error_probability": 0.0,
        "teleportation_fidelity": 0.5,
        "bob_probability_0": 0.5,
        "bob_probability_1": 0.5,
    }
    payload.update(overrides)
    return payload


def test_quantum_scenario_replay_recomputes_saved_result():
    scenario = _quantum_scenario()
    replayed = replay_scenario(scenario)

    assert replayed["workspace"] == "quantum-information"
    assert replayed["teleportation_fidelity"] == pytest.approx(0.5, abs=1e-12)
    assert replayed["bob_probability_0"] == pytest.approx(0.5, abs=1e-12)
    assert replayed["bob_probability_1"] == pytest.approx(0.5, abs=1e-12)

    rows = comparison_rows(scenario, replayed)
    fidelity = next(row for row in rows if row["field"] == "teleportation_fidelity")
    assert fidelity["absolute_difference"] == pytest.approx(0.0, abs=1e-12)


def test_replay_detects_changed_saved_value_without_trusting_it():
    scenario = _quantum_scenario(teleportation_fidelity=0.9)
    replayed = replay_scenario(scenario)
    assert replayed["teleportation_fidelity"] == pytest.approx(0.5, abs=1e-12)

    rows = comparison_rows(scenario, replayed)
    fidelity = next(row for row in rows if row["field"] == "teleportation_fidelity")
    assert fidelity["absolute_difference"] == pytest.approx(0.4, abs=1e-12)


def test_kerr_scenario_replay():
    scenario = {
        "schema_version": 1,
        "horizonlink_version": "0.4.0",
        "workspace": "kerr-rotation",
        "model_level": "established",
        "mass_solar": 10.0,
        "chi": 0.9,
        "polar_angle_deg": 90.0,
        "outer_horizon_radius_m": 0.0,
    }
    replayed = replay_scenario(scenario)
    assert replayed["outer_horizon_radius_m"] > 0.0
    assert replayed["inner_horizon_radius_m"] > 0.0
    assert replayed["static_limit_radius_m"] >= replayed["outer_horizon_radius_m"]


def test_exterior_scenario_replay_and_inverse_outputs():
    scenario = {
        "schema_version": 1,
        "horizonlink_version": "0.4.0",
        "workspace": "exterior-link",
        "model_level": "analogue",
        "mass_solar": 10.0,
        "emitter_radius_rs": 2.0,
        "emitted_frequency_hz": 1.0e9,
        "transmitter_power_w": 1.0e8,
        "receiver_distance_m": 1.0e9,
        "aperture_area_m2": 100.0,
        "bandwidth_hz": 1.0e6,
        "system_temperature_k": 50.0,
        "integration_time_s": 10.0,
        "target_integrated_snr": 5.0,
    }
    replayed = replay_scenario(scenario)
    assert replayed["received_signal_power_w"] > 0.0
    assert replayed["integrated_radiometer_snr"] > 0.0
    assert replayed["required_transmitter_power_w"] > 0.0
    assert replayed["required_collecting_area_m2"] > 0.0
    assert replayed["required_integration_time_s"] > 0.0
    assert replayed["maximum_receiver_distance_m"] > 0.0


def test_scenario_schema_and_workspace_are_strictly_validated():
    with pytest.raises(ScenarioError, match="schema_version"):
        validate_scenario(_quantum_scenario(schema_version=99))
    with pytest.raises(ScenarioError, match="workspace"):
        validate_scenario(_quantum_scenario(workspace="mystery"))


def test_nonfinite_scenario_input_is_rejected():
    with pytest.raises(ScenarioError, match="finite"):
        replay_scenario(_quantum_scenario(theta_rad=float("nan")))
