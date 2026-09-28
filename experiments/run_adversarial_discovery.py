"""Calculate -> sweep -> discover -> cross-validate -> null-test -> falsify.

A candidate survives only if it passes multiple independent numerical screens.
Survival means "worth investigating", never "new physical law".
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import replace

from horizonlink.lab import LabInput, run_lab
from horizonlink.lab.cross_validation import validate_pair
from horizonlink.lab.discovery import scan_table
from horizonlink.lab.falsify import falsify_candidate
from horizonlink.lab.learned_methods import flatten_report
from horizonlink.lab.null_tests import permutation_significance
from horizonlink.lab.provenance import rank_candidate


def values(start: float, stop: float, points: int, log_offset: bool):
    if points < 12:
        raise ValueError("at least 12 points required for adversarial discovery")
    if log_offset:
        if start <= 1 or stop <= 1:
            raise ValueError("log-offset radius bounds must exceed 1")
        lo, hi = math.log10(start - 1), math.log10(stop - 1)
        return [1 + 10 ** (lo + (hi - lo) * i / (points - 1)) for i in range(points)]
    return [start + (stop - start) * i / (points - 1) for i in range(points)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--parameter", default="emitter_radius_rs")
    p.add_argument("--start", type=float, default=1.000001)
    p.add_argument("--stop", type=float, default=1.1)
    p.add_argument("--points", type=int, default=32)
    p.add_argument("--threshold", type=float, default=0.9995)
    p.add_argument("--top", type=int, default=12)
    p.add_argument("--permutations", type=int, default=100)
    p.add_argument("--log-offset", action="store_true")
    a = p.parse_args()

    sweep = values(a.start, a.stop, a.points, a.log_offset)
    base = LabInput()
    reports = [run_lab(replace(base, **{a.parameter: value})) for value in sweep]
    rows = [flatten_report(report) for report in reports]
    raw = scan_table(rows, a.threshold)
    ranked = [rank_candidate(c.as_dict()) for c in raw]
    ranked.sort(key=lambda c: (c["interest_score"], c["score"]), reverse=True)

    survivors = []
    rejected = []
    for candidate in ranked[: a.top]:
        x_name, y_name, model = candidate["x"], candidate["y"], candidate["model"]
        xs = [row[x_name] for row in rows]
        ys = [row[y_name] for row in rows]
        cv = next((r for r in validate_pair(x_name, y_name, xs, ys) if r["model"] == model), None)
        try:
            null = permutation_significance(x_name, y_name, xs, ys, model=model,
                                            permutations=a.permutations, seed=17)
        except ValueError as exc:
            null = {"error": str(exc), "empirical_p_value": 1.0}
        try:
            fals = falsify_candidate(x=x_name, y=y_name, model=model,
                                     sweep_parameter=a.parameter, sweep_values=sweep, base=base)
        except Exception as exc:
            fals = {"error": f"{type(exc).__name__}: {exc}"}

        passes = bool(cv and cv["passes_1pct"] and null["empirical_p_value"] <= 0.05)
        record = {"candidate": candidate, "cross_validation": cv, "null_test": null,
                  "falsification": fals, "passes_statistical_screens": passes}
        (survivors if passes else rejected).append(record)

    print(json.dumps({
        "cycle": ["calculate", "sweep", "search_for_structure", "test", "falsify"],
        "sweep_parameter": a.parameter,
        "points": len(sweep),
        "raw_candidate_count": len(raw),
        "screened": min(a.top, len(ranked)),
        "survivors": survivors,
        "rejected": rejected,
        "next_step": "Build new targeted calculations only around survivors, then repeat over wider domains.",
        "warning": "A survivor is a numerical research lead, not evidence of new physics by itself."
    }, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
