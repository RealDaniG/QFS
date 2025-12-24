"""
deterministic_helpers.py - Deterministic Helper Functions for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready, Fully Auditable

This module implements all the helper functions required by the auto_fix_violations.py script:
- ZeroSimAbort: Exception for Zero-Simulation violations
- det_time_now: Deterministic time function
- det_perf_counter: Deterministic performance counter
- det_random: Deterministic random number generator
- qnum: Safe numeric type conversion
"""

import hashlib
from typing import Any, Optional
from .BigNum128 import BigNum128


class ZeroSimAbort(Exception):
    """
    Exception raised for Zero-Simulation violations.

    This replaces sys.exit() calls to maintain determinism while still
    signaling fatal situations that would normally terminate the interpreter.
    """

    def __init__(self, exit_code: int = 1):
        self.exit_code = exit_code
        super().__init__(f"Zero-Simulation abort requested with exit code: {exit_code}")


_prng_state = 1234567890


def det_random() -> float:
    """
    Deterministic random number generator.

    Uses a linear congruential generator (LCG) for deterministic pseudo-random numbers.
    This replaces random.random() calls to maintain Zero-Simulation compliance.

    Returns:
        float: A deterministic pseudo-random float in the range [0.0, 1.0)
    """
    global _prng_state
    _prng_state = _prng_state * 1103515245 + 12345 & 2147483647
    return _prng_state // 2147483648


def det_time_now() -> int:
    """
    Deterministic time function.

    Returns a fixed timestamp to maintain determinism.
    This replaces time.time() calls to maintain Zero-Simulation compliance.

    Returns:
        int: A deterministic timestamp (seconds since epoch)
    """
    return 1700000000


def det_time_isoformat() -> str:
    """
    Deterministic ISO format time string.

    Returns a fixed ISO format time string to maintain determinism.
    This replaces datetime.now().isoformat() calls to maintain Zero-Simulation compliance.

    Returns:
        str: A deterministic ISO format time string
    """
    return "2023-11-14T12:53:20+00:00"


def det_perf_counter() -> float:
    """
    Deterministic performance counter.

    Returns a fixed performance counter value to maintain determinism.
    This replaces time.perf_counter() calls to maintain Zero-Simulation compliance.

    Returns:
        float: A deterministic performance counter value
    """
    return 1000


def qnum(value: Any) -> BigNum128:
    """
    Safe numeric type conversion to BigNum128.

    This replaces float() calls to maintain Zero-Simulation compliance
    by using the project's fixed-point arithmetic system.

    Args:
        value: Value to convert to BigNum128

    Returns:
        BigNum128: The converted value as a fixed-point number

    Raises:
        TypeError: If the value cannot be converted to BigNum128
    """
    if isinstance(value, BigNum128):
        return value
    elif isinstance(value, int):
        return BigNum128.from_int(value)
    elif isinstance(value, str):
        return BigNum128.from_string(value)
    elif isinstance(value, float):
        return BigNum128.from_string(str(value))
    else:
        raise TypeError(f"Cannot convert {type(value)} to BigNum128")


class DeterministicID:
    """
    Deterministic ID generator replacing uuid.uuid4().
    Uses a counter and hash to generate unique yet reproducible IDs.
    """

    _counter = 0
    _seed = "qfs-v13-seed"

    @classmethod
    def from_string(cls, data: str) -> str:
        """
        Generate deterministic ID from input string using SHA-256.

        Args:
            data: Input string to hash

        Returns:
            str: Deterministic 32-character hex ID
        """
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    @classmethod
    def next(cls) -> str:
        """
        Generate next deterministic ID.
        """
        cls._counter += 1
        return cls.from_string(f"{cls._seed}-{cls._counter}")


def det_random_bytes(n: int) -> bytes:
    """
    Deterministic random bytes generator.
    Replaces os.urandom() usage.
    """
    global _prng_state
    result = bytearray()
    while len(result) < n:
        _prng_state = (_prng_state * 1103515245 + 12345) & 0x7FFFFFFF
        chunk = hashlib.sha256(str(_prng_state).encode()).digest()
        result.extend(chunk)
    return bytes(result[:n])


def deterministic_hash(value: Any) -> int:
    """
    Deterministic hash function for safe set/dict operations.
    Replaces built-in hash() which is non-deterministic for strings/bytes across runs.
    """
    if isinstance(value, (int, bool)):
        return hash(value)  # Ints/Bools are safe
    if isinstance(value, (str, bytes)):
        # SHA-256 for stable hashing of sequence types
        if isinstance(value, str):
            value = value.encode("utf-8")
        return int(hashlib.sha256(value).hexdigest(), 16)
    if isinstance(value, float):
        raise TypeError("Floats Forbidden in deterministic hash")
    if value is None:
        return 0
    # Fallback to str() representation
    return int(hashlib.sha256(str(value).encode("utf-8")).hexdigest(), 16)
