import pytest

from horizonlink.metrics.information import bit_error_rate, bit_error_stats


def test_bit_error_rate_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        bit_error_rate([0, 1], [0])


def test_all_erased_bits_are_not_reported_as_zero_error():
    stats = bit_error_stats([0, 1], [-1, -1])
    assert stats.transmitted == 2
    assert stats.received == 0
    assert stats.erased == 2
    assert stats.errors == 0
    assert stats.erasure_rate == pytest.approx(1.0)
    assert stats.conditional_ber is None
    assert bit_error_rate([0, 1], [-1, -1]) is None


def test_conditional_ber_and_erasure_rate_are_both_exposed():
    stats = bit_error_stats([0, 1, 1, 0], [0, -1, 0, 0])
    assert stats.received == 3
    assert stats.erased == 1
    assert stats.errors == 1
    assert stats.conditional_ber == pytest.approx(1.0 / 3.0)
    assert stats.erasure_rate == pytest.approx(0.25)


def test_invalid_symbols_are_rejected():
    with pytest.raises(ValueError):
        bit_error_stats([0, 2], [0, 1])
    with pytest.raises(ValueError):
        bit_error_stats([0, 1], [0, 9])
