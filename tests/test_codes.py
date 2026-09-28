import numpy as np
import pytest

from horizonlink.codes.hamming74 import decode as hamming_decode
from horizonlink.codes.hamming74 import encode as hamming_encode
from horizonlink.codes.repetition import decode as repetition_decode
from horizonlink.codes.repetition import encode as repetition_encode


def test_repetition_round_trip_and_majority_correction():
    bits = np.array([0, 1, 1, 0], dtype=np.int8)
    encoded = repetition_encode(bits, repetitions=3)
    assert encoded.tolist() == [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0]

    damaged = encoded.copy()
    damaged[[0, 4, 7, 11]] ^= 1
    assert np.array_equal(repetition_decode(damaged, repetitions=3), bits)


def test_repetition_requires_positive_odd_factor():
    with pytest.raises(ValueError, match="positive odd"):
        repetition_encode([0, 1], repetitions=2)
    with pytest.raises(ValueError, match="divisible"):
        repetition_decode([0, 0, 0, 1], repetitions=3)


def test_hamming_known_codeword():
    encoded = hamming_encode([1, 0, 1, 1])
    assert encoded.tolist() == [0, 1, 1, 0, 0, 1, 1]
    assert hamming_decode(encoded).tolist() == [1, 0, 1, 1]


@pytest.mark.parametrize("error_position", range(7))
def test_hamming_corrects_every_single_bit_position(error_position):
    source = np.array([1, 0, 1, 1], dtype=np.int8)
    encoded = hamming_encode(source)
    encoded[error_position] ^= 1
    assert np.array_equal(hamming_decode(encoded), source)


def test_hamming_round_trip_multiple_blocks():
    bits = np.array([0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1], dtype=np.int8)
    assert np.array_equal(hamming_decode(hamming_encode(bits)), bits)


def test_hamming_rejects_incomplete_blocks():
    with pytest.raises(ValueError, match="divisible by 4"):
        hamming_encode([0, 1, 0])
    with pytest.raises(ValueError, match="divisible by 7"):
        hamming_decode([0, 1, 0])


def test_codes_reject_nonbinary_inputs():
    with pytest.raises(ValueError):
        repetition_encode([0, 2, 1])
    with pytest.raises(ValueError):
        hamming_encode([0, 1, 2, 0])
