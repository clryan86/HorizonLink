import pytest

from horizonlink.simulation.monte_carlo import run_bsc_trials


def test_monte_carlo_tracks_expected_error_rate_and_precision():
    result = run_bsc_trials(0.1, trials=40, bits_per_trial=2000, seed=123)
    assert result.mean_bit_error_rate == pytest.approx(0.1, abs=0.02)
    assert result.std_bit_error_rate >= 0.0
    assert result.standard_error > 0.0
    assert result.confidence == 0.95
    assert result.confidence_interval_low < result.mean_bit_error_rate
    assert result.confidence_interval_high > result.mean_bit_error_rate
    assert result.confidence_interval_low < 0.1 < result.confidence_interval_high
    assert result.confidence_interval_half_width > 0.0
    assert result.relative_standard_error > 0.0
    assert result.relative_confidence_interval_half_width > 0.0
    assert result.relative_tolerance == 0.05
    assert result.absolute_tolerance == 1e-4
    assert isinstance(result.converged, bool)


def test_monte_carlo_is_reproducible():
    first = run_bsc_trials(0.2, trials=10, bits_per_trial=500, seed=7)
    second = run_bsc_trials(0.2, trials=10, bits_per_trial=500, seed=7)
    assert first == second


def test_custom_precision_thresholds_are_propagated():
    result = run_bsc_trials(
        0.1,
        trials=20,
        bits_per_trial=5000,
        seed=12,
        relative_tolerance=0.10,
        absolute_tolerance=0.0,
    )
    assert result.relative_tolerance == 0.10
    assert result.absolute_tolerance == 0.0
    assert result.converged is True


def test_single_trial_reports_unknown_uncertainty_and_convergence():
    result = run_bsc_trials(0.2, trials=1, bits_per_trial=500, seed=7)
    assert result.standard_error is None
    assert result.confidence_interval_low is None
    assert result.confidence_interval_high is None
    assert result.confidence_interval_half_width is None
    assert result.relative_standard_error is None
    assert result.relative_confidence_interval_half_width is None
    assert result.converged is None


def test_zero_noise_has_zero_uncertainty_after_multiple_trials():
    result = run_bsc_trials(0.0, trials=4, bits_per_trial=500, seed=7)
    assert result.mean_bit_error_rate == 0.0
    assert result.standard_error == 0.0
    assert result.confidence_interval_low == 0.0
    assert result.confidence_interval_high == 0.0
    assert result.confidence_interval_half_width == 0.0
    assert result.relative_standard_error == 0.0
    assert result.relative_confidence_interval_half_width == 0.0
    assert result.converged is True


def test_invalid_trial_count_probability_and_tolerances():
    with pytest.raises(ValueError):
        run_bsc_trials(0.1, trials=0)
    with pytest.raises(ValueError):
        run_bsc_trials(float("nan"))
    with pytest.raises(ValueError):
        run_bsc_trials(0.1, relative_tolerance=-1.0)
