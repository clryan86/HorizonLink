import json
from pathlib import Path

import pytest

from horizonlink.scenarios import comparison_rows, replay_scenario

SCENARIO_DIR = Path("examples/scenarios")


@pytest.mark.parametrize(
    "filename",
    ["exterior-link.json", "kerr-rotation.json", "quantum-information.json"],
)
def test_example_scenarios_replay_without_drift(filename):
    scenario = json.loads((SCENARIO_DIR / filename).read_text(encoding="utf-8"))
    replayed = replay_scenario(scenario)
    rows = comparison_rows(scenario, replayed)

    assert rows
    assert max(row["relative_difference"] for row in rows) <= 1.0e-12


def test_example_scenarios_cover_all_supported_workspaces():
    workspaces = {
        json.loads(path.read_text(encoding="utf-8"))["workspace"]
        for path in SCENARIO_DIR.glob("*.json")
    }
    assert workspaces == {"exterior-link", "kerr-rotation", "quantum-information"}
