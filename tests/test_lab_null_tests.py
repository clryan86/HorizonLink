from horizonlink.lab.null_tests import permutation_significance


def test_exact_power_law_beats_shuffled_null():
    xs = [float(i) for i in range(1, 25)]
    ys = [2.0 * x ** 2 for x in xs]
    result = permutation_significance("x", "y", xs, ys, permutations=50, seed=7)
    assert result["observed_score"] > 0.999999999
    assert result["empirical_p_value"] <= 2 / 51
