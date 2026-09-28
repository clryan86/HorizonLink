from horizonlink.lab.runner import LabInput
from horizonlink.lab.sweep import discover_invariants, sweep_rows


def test_controlled_sweep_has_expected_point_count():
    rows = sweep_rows(
        LabInput(),
        masses=(3.0, 10.0),
        radii_rs=(1.01, 2.0),
        frequencies_hz=(1e6, 1e9),
    )
    assert len(rows) == 8
    assert all("input.mass_solar" in row for row in rows)


def test_discovery_returns_candidates_and_warning():
    result = discover_invariants(max_terms=2, max_results=10, scatter_threshold=1e-8)
    assert result["points"] == 36
    assert isinstance(result["candidates"], list)
    assert "independent" in result["warning"]
