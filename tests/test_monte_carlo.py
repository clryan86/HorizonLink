import pytest

from horizonlink.simulation.monte_carlo import run_bsc_trials


def test_monte_carlo_tracks_expected_error_rate():
    result = run_bsc_trials(0.1, trials=40, bits_per_trial=2000, seed=123)
    assert result.mean_bit_error_rate == pytest.approx(0.1, abs=0.02)
    assert result.std_bit_error_rate >= 0.0


def test_monte_carlo_is_reproducible():
    first = run_bsc_trials(0.2, trials=10, bits_per_trial=500, seed=7)
    second = run_bsc_trials(0.2, trials=10, bits_per_trial=500, seed=7)
    assert first == second


def test_invalid_trial_count():
    with pytest.raises(ValueError):
        run_bsc_trials(0.1, trials=0)
