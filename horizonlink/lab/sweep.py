"""Controlled HorizonLink parameter sweeps for discovery experiments."""
from __future__ import annotations

from dataclasses import replace
from itertools import product
from typing import Iterable

from .dimensionless_search import search_invariants
from .runner import LabInput, run_lab


def flatten_report(inp: LabInput) -> dict[str, float]:
    """Run one lab point and flatten successful numeric outputs."""
    report = run_lab(inp)
    row: dict[str, float] = {}
    for result in report.calculations:
        if result.status != "ok":
            continue
        for key, value in result.values.items():
            if isinstance(value, (int, float)):
                row[f"{result.name}.{key}"] = float(value)
    return row


def sweep_rows(
    base: LabInput,
    *,
    masses: Iterable[float] = (3.0, 10.0, 30.0),
    radii_rs: Iterable[float] = (1.001, 1.01, 1.1, 2.0),
    frequencies_hz: Iterable[float] = (1e6, 1e9, 1e12),
) -> list[dict[str, float]]:
    """Evaluate a controlled Cartesian sweep."""
    rows = []
    for mass, radius, frequency in product(masses, radii_rs, frequencies_hz):
        inp = replace(
            base,
            mass_solar=float(mass),
            emitter_radius_rs=float(radius),
            emitted_hz=float(frequency),
        )
        row = flatten_report(inp)
        row["input.mass_solar"] = float(mass)
        row["input.emitter_radius_rs"] = float(radius)
        row["input.emitted_hz"] = float(frequency)
        rows.append(row)
    return rows


def discover_invariants(
    base: LabInput | None = None,
    *,
    max_terms: int = 3,
    max_results: int = 50,
    scatter_threshold: float = 1e-10,
) -> dict:
    """Sweep the lab and return bounded low-scatter product candidates."""
    rows = sweep_rows(base or LabInput())
    candidates = search_invariants(
        rows,
        max_terms=max_terms,
        max_results=max_results,
        scatter_threshold=scatter_threshold,
    )
    return {
        "points": len(rows),
        "candidates": candidates,
        "warning": (
            "Candidates may be identities or consequences of shared formulas; "
            "independent derivation and falsification are required."
        ),
    }
