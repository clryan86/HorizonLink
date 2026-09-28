import pytest

from horizonlink.simulation.ecc_benchmark import run_ecc_benchmark


def test_ecc_benchmark_is_reproducible():
    first = run_ecc_benchmark(0.05, trials=8, bits_per_trial=4000, seed=42)
    second = run_ecc_benchmark(0.05, trials=8, bits_per_trial=4000, seed=42)
    assert first == second


def test_zero_noise_gives_zero_ber_for_every_scheme():
    result = run_ecc_benchmark(0.0, trials=4, bits_per_trial=400, seed=7)
    assert result.uncoded_mean_ber == 0.0
    assert result.repetition3_mean_ber == 0.0
    assert result.hamming74_mean_ber == 0.0


def test_coding_improves_payload_ber_at_low_flip_probability():
    result = run_ecc_benchmark(0.05, trials=20, bits_per_trial=4000, seed=123)
    assert result.repetition3_mean_ber < result.uncoded_mean_ber
    assert result.hamming74_mean_ber < result.uncoded_mean_ber


def test_result_reports_redundancy_costs():
    payload = run_ecc_benchmark(0.01, trials=2, bits_per_trial=400, seed=1).as_dict()
    assert payload["uncoded_code_rate"] == 1.0
    assert payload["repetition3_code_rate"] == pytest.approx(1.0 / 3.0)
    assert payload["hamming74_code_rate"] == pytest.approx(4.0 / 7.0)


def test_invalid_benchmark_inputs_are_rejected():
    with pytest.raises(ValueError):
        run_ecc_benchmark(float("nan"))
    with pytest.raises(ValueError):
        run_ecc_benchmark(-0.1)
    with pytest.raises(ValueError):
        run_ecc_benchmark(0.1, trials=0)
    with pytest.raises(ValueError, match="divisible by 4"):
        run_ecc_benchmark(0.1, bits_per_trial=401)
