from horizonlink.lab.cross_validation import validate_pair


def test_power_law_generalizes_to_holdout_points():
    xs = [float(i) for i in range(1, 33)]
    ys = [3.25 * x ** 1.5 for x in xs]
    results = validate_pair("x", "y", xs, ys)
    power = next(item for item in results if item["model"] == "power_law")
    assert power["passes_1pct"]
    assert power["holdout_nrmse"] < 1e-10


def test_rejects_too_few_points():
    try:
        validate_pair("x", "y", [1.0] * 7, [2.0] * 7)
    except ValueError:
        pass
    else:
        raise AssertionError("expected minimum sample guard")
