import json

import pytest

from horizonlink.cli import main


def test_radius_command(capsys):
    assert main(["radius", "1"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert 2900.0 < payload["schwarzschild_radius_m"] < 3000.0


def test_bsc_capacity_command(capsys):
    assert main(["bsc-capacity", "0.0"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["capacity_bits_per_use"] == 1.0


def test_link_budget_command(capsys):
    assert main(["link-budget", "10", "2", "1000000", "1000000000"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert 0.0 < payload["redshifted_frequency_hz"] < 1.0e9
    assert 0.0 < payload["received_power_fraction"] < 1.0


def test_link_design_command(capsys):
    argv = [
        "link-design",
        "10",
        "2",
        "1000000000",
        "100000000",
        "50",
        "1000000",
        "10",
        "--aperture-area-m2",
        "100",
        "--target-snr",
        "5",
    ]
    assert main(argv) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["target_integrated_snr"] == 5.0
    assert payload["required_transmitter_power_w"] > 0.0
    assert payload["required_collecting_area_m2"] > 0.0
    assert payload["required_integration_time_s"] > 0.0
    assert payload["maximum_receiver_distance_m"] > 0.0
    assert payload["current_integrated_snr"] > 0.0


def test_ecc_benchmark_command(capsys):
    assert main(["ecc-benchmark", "0.05", "--trials", "4", "--bits", "4000", "--seed", "7"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["flip_probability"] == 0.05
    assert payload["repetition3_code_rate"] == pytest.approx(1.0 / 3.0)
    assert payload["hamming74_code_rate"] == pytest.approx(4.0 / 7.0)
    assert payload["repetition3_mean_ber"] < payload["uncoded_mean_ber"]
    assert payload["hamming74_mean_ber"] < payload["uncoded_mean_ber"]


def test_scenario_replay_command(tmp_path, capsys):
    scenario = {
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
    path = tmp_path / "scenario.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")

    assert main(["scenario-replay", str(path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["workspace"] == "quantum-information"
    assert payload["recomputed"]["teleportation_fidelity"] == pytest.approx(0.5)
    assert payload["comparison"]


def test_scenario_replay_missing_file_is_clean_cli_error(tmp_path, capsys):
    path = tmp_path / "missing.json"
    with pytest.raises(SystemExit) as exc:
        main(["scenario-replay", str(path)])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "No such file" in captured.err
    assert "Traceback" not in captured.err


def test_cli_rejects_nan_before_calculation(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["radius", "nan"])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "finite" in captured.err
    assert captured.out == ""


def test_cli_reports_validation_error_without_traceback(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["radius", "-1"])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "positive" in captured.err
    assert "Traceback" not in captured.err
