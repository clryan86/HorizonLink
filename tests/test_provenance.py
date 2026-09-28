import json

import pytest

from horizonlink.provenance import (
    experiment_metadata,
    metadata_sidecar_path,
    write_csv_with_metadata,
)


def test_experiment_metadata_contains_reproducibility_fields(monkeypatch):
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    metadata = experiment_metadata(
        experiment="unit-test",
        model_level="analogue",
        inputs={"mass_solar": 10.0},
        seed=42,
    )
    assert metadata["experiment"] == "unit-test"
    assert metadata["model_level"] == "analogue"
    assert metadata["seed"] == 42
    assert metadata["software"]["git_commit"] == "abc123"
    assert metadata["software"]["python_version"]
    assert metadata["software"]["numpy_version"]


def test_csv_and_metadata_sidecar_are_written(tmp_path):
    path = tmp_path / "results" / "example.csv"
    metadata = experiment_metadata(
        experiment="unit-test",
        model_level="established",
        inputs={"x": 1.0},
    )
    data_path, sidecar = write_csv_with_metadata(
        path,
        fieldnames=["x", "y"],
        rows=[{"x": 1.0, "y": 2.0}],
        metadata=metadata,
    )
    assert data_path.read_text(encoding="utf-8").splitlines() == ["x,y", "1.0,2.0"]
    saved_metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert saved_metadata["experiment"] == "unit-test"
    assert sidecar == metadata_sidecar_path(path)


def test_nonfinite_row_cannot_overwrite_existing_result(tmp_path):
    path = tmp_path / "existing.csv"
    path.write_text("trusted-old-result\n", encoding="utf-8")
    metadata = experiment_metadata(
        experiment="unit-test",
        model_level="analogue",
        inputs={"x": 1.0},
    )

    with pytest.raises(ValueError):
        write_csv_with_metadata(
            path,
            fieldnames=["x"],
            rows=[{"x": float("nan")}],
            metadata=metadata,
        )

    assert path.read_text(encoding="utf-8") == "trusted-old-result\n"
    assert not metadata_sidecar_path(path).exists()
