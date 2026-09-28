"""Reproducibility and safe-output helpers for HorizonLink experiments."""

from __future__ import annotations

import csv
import json
import os
import platform
import subprocess
import sys
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from horizonlink import __version__


def current_git_commit() -> str | None:
    """Return the current Git commit when running from a checkout, else None."""
    env_sha = os.environ.get("GITHUB_SHA")
    if env_sha:
        return env_sha
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2.0,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    commit = result.stdout.strip()
    return commit or None


def experiment_metadata(
    *,
    experiment: str,
    model_level: str,
    inputs: Mapping[str, Any],
    seed: int | None = None,
) -> dict[str, Any]:
    """Build a JSON-serializable provenance record for one experiment."""
    if not experiment.strip():
        raise ValueError("experiment name cannot be empty")
    if model_level not in {"established", "analogue", "speculative-toy"}:
        raise ValueError("model_level must be established, analogue, or speculative-toy")

    return {
        "schema_version": 1,
        "experiment": experiment,
        "model_level": model_level,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": dict(inputs),
        "seed": seed,
        "software": {
            "horizonlink_version": __version__,
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "numpy_version": np.__version__,
            "platform": sys.platform,
            "git_commit": current_git_commit(),
        },
    }


def metadata_sidecar_path(data_path: Path) -> Path:
    """Return ``<filename>.<ext>.metadata.json`` beside a data file."""
    return data_path.with_name(data_path.name + ".metadata.json")


def _atomic_write(path: Path, writer) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            writer(handle)
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(path)
    except Exception:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise


def write_csv_with_metadata(
    path: Path,
    *,
    fieldnames: Sequence[str],
    rows: Iterable[Mapping[str, Any]],
    metadata: Mapping[str, Any],
) -> tuple[Path, Path]:
    """Atomically write CSV data plus a JSON provenance sidecar.

    Rows are materialized before any destination is replaced so errors in row
    generation/serialization cannot truncate an existing experiment result.
    """
    path = Path(path)
    materialized_rows = [dict(row) for row in rows]
    json.dumps(metadata, allow_nan=False)

    def write_csv(handle) -> None:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(materialized_rows)

    sidecar = metadata_sidecar_path(path)

    def write_metadata(handle) -> None:
        json.dump(metadata, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")

    _atomic_write(path, write_csv)
    _atomic_write(sidecar, write_metadata)
    return path, sidecar
