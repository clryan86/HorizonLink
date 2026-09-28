"""Search simple dimensionless products for approximate invariants.

This module deliberately searches a bounded exponent vocabulary rather than
arbitrary symbolic expressions. It is intended to generate hypotheses, not
establish new physical laws.
"""
from __future__ import annotations

from itertools import combinations, product
import math
from typing import Iterable

EXPONENTS = (-2, -1, -0.5, 0.5, 1, 2)


def _positive_finite(values: Iterable[float]) -> bool:
    return all(math.isfinite(float(v)) and float(v) > 0 for v in values)


def _relative_scatter(values: list[float]) -> float:
    logs = [math.log(v) for v in values]
    mean = sum(logs) / len(logs)
    return math.sqrt(sum((x - mean) ** 2 for x in logs) / len(logs))


def search_invariants(
    rows: list[dict[str, float]],
    *,
    fields: list[str] | None = None,
    max_terms: int = 3,
    max_results: int = 50,
    scatter_threshold: float = 1e-8,
) -> list[dict]:
    """Return low-scatter products ``prod(field**exponent)`` across rows.

    Results are scale-invariant because scoring is performed in log space.
    Only positive finite columns are eligible. Constant columns are excluded.
    """
    if len(rows) < 4:
        raise ValueError("at least four rows are required")
    common = set.intersection(*(set(row) for row in rows))
    names = sorted(set(fields or common) & common)
    eligible = []
    for name in names:
        vals = [float(row[name]) for row in rows]
        if not _positive_finite(vals):
            continue
        if max(vals) / min(vals) <= 1 + 1e-12:
            continue
        eligible.append(name)

    found = []
    for terms in range(2, min(max_terms, len(eligible)) + 1):
        for nameset in combinations(eligible, terms):
            columns = [[float(row[n]) for row in rows] for n in nameset]
            for powers in product(EXPONENTS, repeat=terms):
                # Remove equivalent reciprocal duplicates by fixing first sign.
                if powers[0] < 0:
                    continue
                logs = []
                for idx in range(len(rows)):
                    logs.append(sum(p * math.log(col[idx]) for p, col in zip(powers, columns)))
                mean = sum(logs) / len(logs)
                scatter = math.sqrt(sum((v - mean) ** 2 for v in logs) / len(logs))
                if scatter <= scatter_threshold:
                    found.append({
                        "fields": list(nameset),
                        "exponents": list(powers),
                        "log_scatter": scatter,
                        "geometric_mean": math.exp(mean) if abs(mean) < 700 else None,
                        "expression": " * ".join(f"({n})^{p:g}" for n, p in zip(nameset, powers)),
                        "points": len(rows),
                    })
    found.sort(key=lambda x: (x["log_scatter"], len(x["fields"])))
    return found[:max_results]
