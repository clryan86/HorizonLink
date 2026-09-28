import pytest

from horizonlink.metrics.statistics import summarize_samples


def test_summary_reports_mean_standard_error_and_interval():
    summary = summarize_samples([1.0, 2.0, 3.0, 4.0], confidence=0.95)
    assert summary["count"] == 4
    assert summary["mean"] == pytest.approx(2.5)
    assert summary["sample_std"] > 0.0
    assert summary["standard_error"] > 0.0
    assert summary["confidence_interval_low"] < summary["mean"]
    assert summary["confidence_interval_high"] > summary["mean"]
    assert summary["relative_standard_error"] > 0.0


def test_constant_zero_samples_have_zero_relative_standard_error():
    summary = summarize_samples([0.0, 0.0, 0.0])
    assert summary["mean"] == 0.0
    assert summary["standard_error"] == 0.0
    assert summary["relative_standard_error"] == 0.0
    assert summary["confidence_interval_low"] == 0.0
    assert summary["confidence_interval_high"] == 0.0


def test_single_sample_does_not_invent_uncertainty():
    summary = summarize_samples([0.25])
    assert summary["mean"] == 0.25
    assert summary["sample_std"] is None
    assert summary["standard_error"] is None
    assert summary["confidence_interval_low"] is None
    assert summary["confidence_interval_high"] is None


def test_nonfinite_samples_and_invalid_confidence_are_rejected():
    with pytest.raises(ValueError):
        summarize_samples([])
    with pytest.raises(ValueError):
        summarize_samples([1.0, float("nan")])
    with pytest.raises(ValueError):
        summarize_samples([1.0, 2.0], confidence=1.0)
