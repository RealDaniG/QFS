"""
BigNum128.py - Unsigned Fixed-Point Number Class for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready, Fully Auditable
"""

import json
from typing import Any, Dict, List, Union


class BigNum128Error(Exception):
    """Custom exception for BigNum128 operations."""

    pass


class BigNum128:
    """
    Unsigned Fixed-Point number class with 128-bit integer representation and 18 decimal places of precision.
    SCALE = 10^18. Values range from MIN_VALUE (0) to MAX_VALUE (2^128 - 1).
    """

    SCALE = 1000000000000000000
    SCALE_DIGITS = 18
    MAX_VALUE = 340282366920938463463374607431768211455
    MIN_VALUE = 0
    cm = None

    def __init__(self, value: int) -> None:
        self._ensure_cm_initialized()
        if not isinstance(value, int):
            raise TypeError("BigNum128 only accepts integers")
        if value < self.MIN_VALUE or value > self.MAX_VALUE:
            raise OverflowError(
                f"BigNum128 value {value} out of bounds [{self.MIN_VALUE}, {self.MAX_VALUE}]"
            )
        self.value = value

    def _ensure_cm_initialized(self) -> None:
        """Ensure that CertifiedMath is initialized."""
        if self.cm is None:
            from .CertifiedMath import CertifiedMath

            self.cm = CertifiedMath()

    @classmethod
    def from_int(cls, val: int) -> "BigNum128":
        """Creates a BigNum128 from a standard Python integer."""
        if val < 0:
            raise ValueError("Negative values not allowed")
        if not isinstance(val, int):
            raise TypeError(f"Expected int, got {type(val)}")

        # Use plain scalar multiplication to ensure int result
        # val is int, cls.SCALE is int
        scaled_value = val * cls.SCALE

        if scaled_value > cls.MAX_VALUE:
            raise OverflowError("Integer value too large for BigNum128 after scaling")
        return cls(scaled_value)

    @classmethod
    def from_string(cls, s: str) -> "BigNum128":
        """Creates a BigNum128 from a decimal string (e.g., '1.25')."""
        if "-" in s:
            raise ValueError("Negative values not allowed")
        if not isinstance(s, str):
            raise TypeError("Input must be a string")
        s = s.strip()
        if "." in s:
            parts = s.split(".")
            if len(parts) > 2:
                raise ValueError("Input string must contain at most one decimal point")
            integer_part = parts[0] or "0"
            decimal_part = parts[1] or "0"
            if integer_part == "" and decimal_part == "":
                integer_part = "0"
                decimal_part = "0"
            elif integer_part == "":
                integer_part = "0"
            elif decimal_part == "":
                decimal_part = "0"
            if not integer_part.isdigit() or not decimal_part.isdigit():
                raise ValueError("Input string parts must contain only digits")
            if int(integer_part) > cls.MAX_VALUE // cls.SCALE:
                raise OverflowError("Integer part too large for BigNum128")
            if len(decimal_part) > cls.SCALE_DIGITS:
                extra_digits = decimal_part[cls.SCALE_DIGITS :].rstrip("0")
                if extra_digits:
                    raise BigNum128Error(
                        "Input value too small for BigNum128 (underflow)"
                    )
                round_digit = (
                    int(decimal_part[cls.SCALE_DIGITS])
                    if len(decimal_part) > cls.SCALE_DIGITS
                    else 0
                )
                decimal_part_scaled = decimal_part[: cls.SCALE_DIGITS]
                if round_digit >= 5:
                    decimal_value = int(decimal_part_scaled) + 1
                    if decimal_value >= 10**cls.SCALE_DIGITS:
                        integer_part = str(int(integer_part) + 1)
                        if int(integer_part) > cls.MAX_VALUE // cls.SCALE:
                            raise OverflowError("Integer part overflow after rounding")
                        decimal_part_scaled = "0" * cls.SCALE_DIGITS
                    else:
                        decimal_part_scaled = str(decimal_value).zfill(cls.SCALE_DIGITS)
                else:
                    decimal_part_scaled = decimal_part_scaled.ljust(
                        cls.SCALE_DIGITS, "0"
                    )
            else:
                decimal_part_scaled = decimal_part.ljust(cls.SCALE_DIGITS, "0")
            value = int(integer_part) * cls.SCALE + int(decimal_part_scaled)
        else:
            if not s.isdigit():
                raise ValueError("Input string must contain only digits")
            if int(s) > cls.MAX_VALUE // cls.SCALE:
                raise OverflowError("Integer value too large for BigNum128")
            value = int(s) * cls.SCALE
        if value > cls.MAX_VALUE:
            raise OverflowError("Scaled value exceeds BigNum128 capacity")
        return cls(value)

    def to_decimal_string(self, fixed_width: bool = True) -> str:
        """Converts the internal integer value to its fixed-point decimal string representation.

        Args:
            fixed_width: If True, always output 18 fractional digits for full auditability.
                        If False, strip trailing zeros (default behavior).
        """
        raw_str = str(self.value).zfill(self.SCALE_DIGITS + 1)
        integer_part = raw_str[: -self.SCALE_DIGITS] or "0"
        if fixed_width:
            fractional_part = raw_str[-self.SCALE_DIGITS :]
        else:
            fractional_part = raw_str[-self.SCALE_DIGITS :].rstrip("0") or "0"
        return f"{integer_part}.{fractional_part}"

    def __str__(self) -> str:
        """String representation for serialization."""
        return self.to_decimal_string()

    def __repr__(self) -> str:
        decimal_str = self.to_decimal_string()
        return f"BigNum128(raw={self.value}, fp='{decimal_str}')"

    def __lt__(self, other: "BigNum128") -> bool:
        if not isinstance(other, BigNum128):
            return False
        return self.value < other.value

    def __le__(self, other: "BigNum128") -> bool:
        if not isinstance(other, BigNum128):
            return False
        return self.value <= other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BigNum128):
            return False
        return self.value == other.value

    def __gt__(self, other: "BigNum128") -> bool:
        if not isinstance(other, BigNum128):
            return False
        return self.value > other.value

    def __ge__(self, other: "BigNum128") -> bool:
        if not isinstance(other, BigNum128):
            return False
        return self.value >= other.value

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __hash__(self) -> int:
        from .deterministic_helpers import deterministic_hash

        return deterministic_hash(self.value)

    def __add__(self, other: "BigNum128") -> "BigNum128":
        return self.add(other)

    def __sub__(self, other: "BigNum128") -> "BigNum128":
        return self.sub(other)

    def __mul__(self, other: Union["BigNum128", int]) -> "BigNum128":
        return self.mul(other)

    def __truediv__(self, other: "BigNum128") -> "BigNum128":
        return self.div(other)

    def __floordiv__(self, other: "BigNum128") -> "BigNum128":
        return self.div(other)

    def __mod__(self, other: "BigNum128") -> "BigNum128":
        if not isinstance(other, BigNum128):
            raise TypeError("mod requires BigNum128")
        from .CertifiedMath import CertifiedMath

        cm = CertifiedMath()
        return BigNum128(cm.mod(self, other).value)

    def copy(self) -> "BigNum128":
        """Returns a copy of this BigNum128 instance."""
        return BigNum128(self.value)

    @classmethod
    def zero(cls) -> "BigNum128":
        return cls(0)

    @classmethod
    def one(cls) -> "BigNum128":
        return cls(cls.SCALE)

    def add(self, other: "BigNum128") -> "BigNum128":
        """Adds two BigNum128 values."""
        from .CertifiedMath import CertifiedMath

        cm = CertifiedMath()
        # Pass objects (self, other) to cm.add, which returns BigNum128
        result = cm.add(self, other)
        return BigNum128(result.value)

    def sub(self, other: "BigNum128") -> "BigNum128":
        """Subtracts two BigNum128 values."""
        from .CertifiedMath import CertifiedMath

        cm = CertifiedMath()
        result = cm.sub(self, other)
        return result

    def mul(self, other: Union["BigNum128", int]) -> "BigNum128":
        """Multiplies two BigNum128 values or a BigNum128 and an integer."""
        from .CertifiedMath import CertifiedMath

        cm = CertifiedMath()

        # Handle int multiplication (scalar)
        if isinstance(other, int):
            # Scalar multiplication
            return cm.imul(self, other)

        if not isinstance(other, BigNum128):
            raise TypeError(f"Cannot multiply BigNum128 with {type(other)}")

        # Fixed point multiplication
        result = cm.mul(self, other)
        # Verify overflow (cm checks it, but double check bounds if needed)
        if result.value > self.MAX_VALUE:
            raise OverflowError("Multiplication result exceeds BigNum128 capacity")
        return result

    def div(self, other: "BigNum128") -> "BigNum128":
        """Divides two BigNum128 values."""
        if other.value == 0:
            raise ZeroDivisionError("Division by zero")
        from .CertifiedMath import CertifiedMath

        cm = CertifiedMath()
        # div implements fixed point division (a * SCALE // b)
        return cm.div(self, other)
