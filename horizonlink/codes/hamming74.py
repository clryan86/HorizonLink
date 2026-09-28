"""Binary Hamming(7,4) single-error-correcting code.

Codeword positions use the conventional parity locations 1, 2, and 4 with
data bits at positions 3, 5, 6, and 7. The decoder corrects one flipped bit
per seven-bit codeword. Two-or-more-bit errors can be miscorrected, as expected
for an ordinary Hamming(7,4) code without an overall parity bit.
"""

from __future__ import annotations

import numpy as np


def _validated_bits(bits) -> np.ndarray:
    data = np.asarray(bits, dtype=np.int8)
    if data.ndim != 1 or np.any((data != 0) & (data != 1)):
        raise ValueError("bits must be a one-dimensional sequence of 0s and 1s")
    return data


def encode(bits) -> np.ndarray:
    """Encode source bits in groups of four into Hamming(7,4) codewords."""
    data = _validated_bits(bits)
    if data.size % 4 != 0:
        raise ValueError("source bit count must be divisible by 4")
    if data.size == 0:
        return data.copy()

    blocks = data.reshape(-1, 4)
    d1 = blocks[:, 0]
    d2 = blocks[:, 1]
    d3 = blocks[:, 2]
    d4 = blocks[:, 3]

    codewords = np.empty((blocks.shape[0], 7), dtype=np.int8)
    codewords[:, 0] = d1 ^ d2 ^ d4
    codewords[:, 1] = d1 ^ d3 ^ d4
    codewords[:, 2] = d1
    codewords[:, 3] = d2 ^ d3 ^ d4
    codewords[:, 4] = d2
    codewords[:, 5] = d3
    codewords[:, 6] = d4
    return codewords.reshape(-1)


def decode(encoded_bits) -> np.ndarray:
    """Decode Hamming(7,4) codewords, correcting one flipped bit per block."""
    encoded = _validated_bits(encoded_bits)
    if encoded.size % 7 != 0:
        raise ValueError("encoded bit count must be divisible by 7")
    if encoded.size == 0:
        return encoded.copy()

    blocks = encoded.reshape(-1, 7).copy()
    s1 = blocks[:, 0] ^ blocks[:, 2] ^ blocks[:, 4] ^ blocks[:, 6]
    s2 = blocks[:, 1] ^ blocks[:, 2] ^ blocks[:, 5] ^ blocks[:, 6]
    s4 = blocks[:, 3] ^ blocks[:, 4] ^ blocks[:, 5] ^ blocks[:, 6]
    syndrome = s1 + 2 * s2 + 4 * s4

    errored_rows = np.nonzero(syndrome)[0]
    if errored_rows.size:
        errored_columns = syndrome[errored_rows] - 1
        blocks[errored_rows, errored_columns] ^= 1

    return blocks[:, [2, 4, 5, 6]].reshape(-1)
