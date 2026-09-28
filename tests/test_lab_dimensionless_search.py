import math

from horizonlink.lab.dimensionless_search import search_invariants


def test_finds_known_inverse_product_invariant():
    rows = []
    for x in (1.0, 2.0, 4.0, 8.0, 16.0, 32.0):
        rows.append({"x": x, "inverse": 7.0 / x, "noise": x ** 0.3})
    found = search_invariants(rows, fields=["x", "inverse", "noise"], scatter_threshold=1e-12)
    assert any(
        set(item["fields"]) == {"x", "inverse"}
        and math.isclose(item["geometric_mean"], 7.0, rel_tol=1e-12)
        for item in found
    )


def test_requires_enough_rows():
    try:
        search_invariants([{"x": 1.0}] * 3)
    except ValueError:
        pass
    else:
        raise AssertionError("expected row-count guard")
