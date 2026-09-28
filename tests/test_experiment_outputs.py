import csv
import json

import pytest

from experiments.run_ecc_sweep import run as run_ecc_sweep
from experiments.run_teleportation_surface import run as run_surface
from experiments.run_teleportation_sweep import run as run_sweep
from horizonlink.provenance import metadata_sidecar_path


def test_teleportation_sweep_writes_versioned_provenance(tmp_path):
    path = run_sweep(points=5, output_path=str(tmp_path / "sweep.csv"))
    sidecar = metadata_sidecar_path(path)

    assert path.exists()
    assert sidecar.exists()

    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["experiment"] == "teleportation-resource-noise-sweep"
    assert metadata["model_level"] == "analogue"
    assert metadata["inputs"]["points"] == 5
    assert "complete depolarization occurs at p=0.75" in metadata["inputs"][
        "pauli_noise_convention"
    ]
    assert metadata["software"]["horizonlink_version"]

    rows = path.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 6
    probability, fidelity = rows[4].split(",")
    assert float(probability) == pytest.approx(0.75)
    assert float(fidelity) == pytest.approx(0.5, abs=1e-12)


def test_teleportation_surface_writes_expected_grid_and_metadata(tmp_path):
    path = run_surface(
        resource_points=3,
        classical_points=3,
        output_path=str(tmp_path / "surface.csv"),
    )
    sidecar = metadata_sidecar_path(path)

    assert sidecar.exists()
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["experiment"] == "teleportation-quantum-classical-noise-surface"
    assert metadata["inputs"]["resource_points"] == 3
    assert metadata["inputs"]["classical_points"] == 3

    rows = path.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1 + 3 * 3


def test_ecc_sweep_writes_rates_ber_and_provenance(tmp_path):
    path = run_ecc_sweep(
        points=3,
        max_flip_probability=0.1,
        trials=4,
        bits_per_trial=400,
        seed=11,
        output_path=str(tmp_path / "ecc.csv"),
    )
    sidecar = metadata_sidecar_path(path)
    assert sidecar.exists()

    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["experiment"] == "bsc-error-correction-sweep"
    assert metadata["seed"] == 11
    assert metadata["inputs"]["schemes"] == ["uncoded", "repetition-3", "hamming-7-4"]

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    assert float(rows[0]["flip_probability"]) == 0.0
    assert float(rows[0]["uncoded_mean_ber"]) == 0.0
    assert float(rows[0]["repetition3_mean_ber"]) == 0.0
    assert float(rows[0]["hamming74_mean_ber"]) == 0.0
    assert float(rows[-1]["repetition3_code_rate"]) == pytest.approx(1.0 / 3.0)
    assert float(rows[-1]["hamming74_code_rate"]) == pytest.approx(4.0 / 7.0)
