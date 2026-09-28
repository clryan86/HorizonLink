import pytest

from horizonlink.simulation.monte_carlo import run_bsc_trials


def test_monte_carlo_tracks_expected_error_rate():
    result = run_bsc_trials(0.1, trials=40, bits_per_trial=2000, seed=123)
    assert result.mean_bit_error_rate == pytest.approx(0.1, abs=0.02)
    assert result.std_bit_error_rate >= 0.0
    assert result.standard_error > 0.0
    assert result.confidence == 0.95
    assert result.confidence_interval_low < result.mean_bit_error_rate
    assert result.confidence_interval_high > result.mean_bit_error_rate
    assert result.confidence_interval_low < 0.1 < result.confidence_interval_high
    assert result.relative_standard_error > 0.0


def test_monte_carlo_is_reproducible():
    first = run_bsc_trials(0.2, trials=10, bits_per_trial=500, seed=7)
    second = run_bsc_trials(0.2, trials=10, bits_per_trial=500, seed=7)
    assert first == second


def test_single_trial_reports_unknown_uncertainty():
    result = run_bsc_trials(0.2, trials=1, bits_per_trial=500, seed=7)
    assert result.standard_error is None
    assert result.confidence_interval_low is None
    assert result.confidence_interval_high is None
    assert result.relative_standard_error is None


def test_zero_noise_has_zero_uncertainty_after_multiple_trials():
    result = run_bsc_trials(0.0, trials=4, bits_per_trial=500, seed=7)
    assert result.mean_bit_error_rate == 0.0
    assert result.standard_error == 0.0
    assert result.confidence_interval_low == 0.0
    assert result.confidence_interval_high == 0.0
    assert result.relative_standard_error == 0.0


def test_invalid_trial_count_and_probability():
    with pytest.raises(ValueError):
        run_bsc_trials(0.1, trials=0)
    with pytest.raises(ValueError):
        run_bsc_trials(float("nan"))
