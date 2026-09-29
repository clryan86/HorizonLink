import pytest

from horizonlink.metrics.statistics import summarize_samples


def test_summary_reports_mean_standard_error_interval_and_precision():
    summary = summarize_samples([1.0, 2.0, 3.0, 4.0], confidence=0.95)
    assert summary["count"] == 4
    assert summary["mean"] == pytest.approx(2.5)
    assert summary["sample_std"] > 0.0
    assert summary["standard_error"] > 0.0
    assert summary["confidence_interval_low"] < summary["mean"]
    assert summary["confidence_interval_high"] > summary["mean"]
    assert summary["confidence_interval_half_width"] > 0.0
    assert summary["relative_standard_error"] > 0.0
    assert summary["relative_confidence_interval_half_width"] > 0.0
    assert summary["relative_tolerance"] == 0.05
    assert summary["absolute_tolerance"] == 1e-4
    assert summary["converged"] is False


def test_precision_thresholds_can_mark_a_stable_estimate_converged():
    summary = summarize_samples(
        [0.099, 0.100, 0.101, 0.100],
        relative_tolerance=0.05,
        absolute_tolerance=0.0,
    )
    assert summary["relative_confidence_interval_half_width"] < 0.05
    assert summary["converged"] is True


def test_absolute_precision_handles_estimates_near_zero():
    summary = summarize_samples(
        [0.0, 0.0001, 0.0, 0.0001],
        relative_tolerance=0.0,
        absolute_tolerance=0.0001,
    )
    assert summary["confidence_interval_half_width"] <= 0.0001
    assert summary["converged"] is True


def test_constant_zero_samples_have_zero_relative_uncertainty_and_converge():
    summary = summarize_samples([0.0, 0.0, 0.0])
    assert summary["mean"] == 0.0
    assert summary["standard_error"] == 0.0
    assert summary["relative_standard_error"] == 0.0
    assert summary["confidence_interval_low"] == 0.0
    assert summary["confidence_interval_high"] == 0.0
    assert summary["confidence_interval_half_width"] == 0.0
    assert summary["relative_confidence_interval_half_width"] == 0.0
    assert summary["converged"] is True


def test_single_sample_does_not_invent_uncertainty_or_convergence():
    summary = summarize_samples([0.25])
    assert summary["mean"] == 0.25
    assert summary["sample_std"] is None
    assert summary["standard_error"] is None
    assert summary["confidence_interval_low"] is None
    assert summary["confidence_interval_high"] is None
    assert summary["confidence_interval_half_width"] is None
    assert summary["relative_confidence_interval_half_width"] is None
    assert summary["converged"] is None


def test_nonfinite_samples_invalid_confidence_and_tolerances_are_rejected():
    with pytest.raises(ValueError):
        summarize_samples([])
    with pytest.raises(ValueError):
        summarize_samples([1.0, float("nan")])
    with pytest.raises(ValueError):
        summarize_samples([1.0, 2.0], confidence=1.0)
    with pytest.raises(ValueError):
        summarize_samples([1.0, 2.0], relative_tolerance=-0.1)
    with pytest.raises(ValueError):
        summarize_samples([1.0, 2.0], absolute_tolerance=float("inf"))
