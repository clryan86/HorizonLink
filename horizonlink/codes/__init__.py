"""Small auditable error-correcting codes used in HorizonLink benchmarks."""

from .hamming74 import decode as hamming74_decode
from .hamming74 import encode as hamming74_encode
from .repetition import decode as repetition_decode
from .repetition import encode as repetition_encode

__all__ = [
    "hamming74_decode",
    "hamming74_encode",
    "repetition_decode",
    "repetition_encode",
]
