"""
BigNum128.py - Unsigned 128-bit Fixed-Point Number Class for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready, Fully Auditable
"""

import json
import hashlib
from typing import Any, Dict, List

# ------------------------------
# Custom Exceptions
# ------------------------------
class BigNum128Error(Exception):
    """Base error for BigNum128 that should trigger CIR-302"""
    pass

# ------------------------------
# BigNum128: Unsigned 128-bit Fixed-Point
# ------------------------------
class BigNum128:
    """
    Unsigned Fixed-Point number class with 128-bit integer representation and 18 decimal places of precision.
    SCALE = 10^18. Values range from MIN_VALUE (0) to MAX_VALUE (2^128 - 1).
    """
    SCALE = 10**18
    SCALE_DIGITS = 18  # New constant
    MAX_VALUE = 2**128 - 1
    MIN_VALUE = 0  # Unsigned type

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("BigNum128 only accepts integers")
        if value < self.MIN_VALUE or value > self.MAX_VALUE:
            raise OverflowError(
                f"BigNum128 value {value} out of bounds [{self.MIN_VALUE}, {self.MAX_VALUE}]"
            )
        self.value = value

    @classmethod
    def from_int(cls, integer_val: int):
        """Creates a BigNum128 from a standard Python integer."""
        return cls(integer_val * cls.SCALE)

    @classmethod
    def from_string(cls, s: str):
        """Converts a string representation to BigNum128."""
        if not isinstance(s, str):
            raise TypeError("Input must be a string")
        s = s.strip()
        
        # Reject negative inputs (unsigned type)
        if s.startswith('-'):
            raise BigNum128Error("BigNum128 is unsigned; negative values not allowed")
        
        if '.' in s:
            parts = s.split('.')
            if len(parts) > 2:
                raise ValueError("Input string must contain at most one decimal point")
            
            integer_part = parts[0] or "0"
            decimal_part = parts[1] or "0"  # Handle "0." case
            
            # Handle ".0" case
            if integer_part == "" and decimal_part == "":
                integer_part = "0"
                decimal_part = "0"
            elif integer_part == "":
                integer_part = "0"
            elif decimal_part == "":
                decimal_part = "0"
            
            # Validate digits
            if not integer_part.isdigit() or not decimal_part.isdigit():
                raise ValueError("Input string parts must contain only digits")
            
            # Check integer part overflow BEFORE scaling
            if int(integer_part) > cls.MAX_VALUE // cls.SCALE:
                raise OverflowError("Integer part too large for BigNum128")
            
            # Check for underflow - if decimal part has more digits than SCALE_DIGITS and the extra digits are non-zero
            if len(decimal_part) > cls.SCALE_DIGITS:
                # Check if the digits beyond SCALE_DIGITS are non-zero (indicating underflow)
                extra_digits = decimal_part[cls.SCALE_DIGITS:].rstrip('0')
                if extra_digits:
                    raise BigNum128Error("Input value too small for BigNum128 (underflow)")
            
            # Truncate/pad fractional part
            decimal_part_scaled = decimal_part.ljust(cls.SCALE_DIGITS, '0')[:cls.SCALE_DIGITS]
            value = int(integer_part) * cls.SCALE + int(decimal_part_scaled)
    
        else:  # Integer string
            if not s.isdigit():
                raise ValueError("Input string must contain only digits")
            if int(s) > cls.MAX_VALUE // cls.SCALE:
                raise OverflowError("Integer value too large for BigNum128")
            value = int(s) * cls.SCALE
        
        if value > cls.MAX_VALUE:
            raise OverflowError("Scaled value exceeds BigNum128 capacity")
        
        return cls(value)

    def to_decimal_string(self) -> str:
        """Converts the internal integer value to its fixed-point decimal string representation."""
        raw_str = str(self.value).zfill(self.SCALE_DIGITS + 1)
        integer_part = raw_str[:-self.SCALE_DIGITS] or "0"
        fractional_part = raw_str[-self.SCALE_DIGITS:].rstrip('0') or '0'
        return f"{integer_part}.{fractional_part}"

    def __str__(self):
        """String representation for serialization."""
        return self.to_decimal_string()

    def __repr__(self):
        # Enhance repr to show both raw value and fixed-point value for debugging
        decimal_str = self.to_decimal_string()
        return f"BigNum128(raw={self.value}, fp='{decimal_str}')"

    # Comparison operators (safe for use in HSMF logic)
    def __eq__(self, other):
        if not isinstance(other, BigNum128):
            return False
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, BigNum128):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    def __ne__(self, other):
        return not self == other
"""
BigNum128.py - Unsigned 128-bit Fixed-Point Number Class for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready, Fully Auditable
"""

import json
import hashlib
from typing import Any, Dict, List

# ------------------------------
# Custom Exceptions
# ------------------------------
class BigNum128Error(Exception):
    """Base error for BigNum128 that should trigger CIR-302"""
    pass

# ------------------------------
# BigNum128: Unsigned 128-bit Fixed-Point
# ------------------------------
class BigNum128:
    """
    Unsigned Fixed-Point number class with 128-bit integer representation and 18 decimal places of precision.
    SCALE = 10^18. Values range from MIN_VALUE (0) to MAX_VALUE (2^128 - 1).
    """
    SCALE = 10**18
    SCALE_DIGITS = 18  # New constant
    MAX_VALUE = 2**128 - 1
    MIN_VALUE = 0  # Unsigned type

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("BigNum128 only accepts integers")
        if value < self.MIN_VALUE or value > self.MAX_VALUE:
            raise OverflowError(
                f"BigNum128 value {value} out of bounds [{self.MIN_VALUE}, {self.MAX_VALUE}]"
            )
        self.value = value

    @classmethod
    def from_int(cls, integer_val: int):
        """Creates a BigNum128 from a standard Python integer."""
        return cls(integer_val * cls.SCALE)

    @classmethod
    def from_string(cls, s: str):
        """Converts a string representation to BigNum128."""
        if not isinstance(s, str):
            raise TypeError("Input must be a string")
        s = s.strip()
        
        # Reject negative inputs (unsigned type)
        if s.startswith('-'):
            raise BigNum128Error("BigNum128 is unsigned; negative values not allowed")
        
        if '.' in s:
            parts = s.split('.')
            if len(parts) > 2:
                raise ValueError("Input string must contain at most one decimal point")
            
            integer_part = parts[0] or "0"
            decimal_part = parts[1] or "0"  # Handle "0." case
            
            # Handle ".0" case
            if integer_part == "" and decimal_part == "":
                integer_part = "0"
                decimal_part = "0"
            elif integer_part == "":
                integer_part = "0"
            elif decimal_part == "":
                decimal_part = "0"
            
            # Validate digits
            if not integer_part.isdigit() or not decimal_part.isdigit():
                raise ValueError("Input string parts must contain only digits")
            
            # Check integer part overflow BEFORE scaling
            if int(integer_part) > cls.MAX_VALUE // cls.SCALE:
                raise OverflowError("Integer part too large for BigNum128")
            
            # Check for underflow - if decimal part has more digits than SCALE_DIGITS and the extra digits are non-zero
            if len(decimal_part) > cls.SCALE_DIGITS:
                # Check if the digits beyond SCALE_DIGITS are non-zero (indicating underflow)
                extra_digits = decimal_part[cls.SCALE_DIGITS:].rstrip('0')
                if extra_digits:
                    raise BigNum128Error("Input value too small for BigNum128 (underflow)")
            
            # Truncate/pad fractional part
            decimal_part_scaled = decimal_part.ljust(cls.SCALE_DIGITS, '0')[:cls.SCALE_DIGITS]
            value = int(integer_part) * cls.SCALE + int(decimal_part_scaled)
    
        else:  # Integer string
            if not s.isdigit():
                raise ValueError("Input string must contain only digits")
            if int(s) > cls.MAX_VALUE // cls.SCALE:
                raise OverflowError("Integer value too large for BigNum128")
            value = int(s) * cls.SCALE
        
        if value > cls.MAX_VALUE:
            raise OverflowError("Scaled value exceeds BigNum128 capacity")
        
        return cls(value)

    def to_decimal_string(self) -> str:
        """Converts the internal integer value to its fixed-point decimal string representation."""
        raw_str = str(self.value).zfill(self.SCALE_DIGITS + 1)
        integer_part = raw_str[:-self.SCALE_DIGITS] or "0"
        fractional_part = raw_str[-self.SCALE_DIGITS:].rstrip('0') or '0'
        return f"{integer_part}.{fractional_part}"

    def __str__(self):
        """String representation for serialization."""
        return self.to_decimal_string()

    def __repr__(self):
        # Enhance repr to show both raw value and fixed-point value for debugging
        decimal_str = self.to_decimal_string()
        return f"BigNum128(raw={self.value}, fp='{decimal_str}')"

    # Comparison operators (safe for use in HSMF logic)
    def __eq__(self, other):
        if not isinstance(other, BigNum128):
            return False
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, BigNum128):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    def __ne__(self, other):
        return not self == other

    # Zero/One constants (for convenience in HSMF logic)
    @classmethod
    def zero(cls):
        return cls(0)

    @classmethod
    def one(cls):
        return cls(cls.SCALE)

    # ------------------------------
    # Arithmetic Operations
    # ------------------------------
    def add(self, other: 'BigNum128') -> 'BigNum128':
        """Adds two BigNum128 values."""
        if not isinstance(other, BigNum128):
            raise TypeError("add requires BigNum128")
        new_val = self.value + other.value
        if new_val > self.MAX_VALUE:
            raise OverflowError("BigNum128 addition overflow")
        return BigNum128(new_val)

    def sub(self, other: 'BigNum128') -> 'BigNum128':
        """Subtracts two BigNum128 values."""
        if not isinstance(other, BigNum128):
            raise TypeError("sub requires BigNum128")
        new_val = self.value - other.value
        if new_val < self.MIN_VALUE:
            raise ValueError("BigNum128 subtraction underflow (result negative)")
        return BigNum128(new_val)

    def mul(self, other: 'BigNum128') -> 'BigNum128':
        """Multiplies two BigNum128 values."""
        if not isinstance(other, BigNum128):
            raise TypeError("mul requires BigNum128")
        # Fixed-point multiplication: (a * b) / SCALE
        new_val = (self.value * other.value) // self.SCALE
        if new_val > self.MAX_VALUE:
            raise OverflowError("BigNum128 multiplication overflow")
        return BigNum128(new_val)

    def div(self, other: 'BigNum128') -> 'BigNum128':
        """Divides two BigNum128 values (floor division)."""
        if not isinstance(other, BigNum128):
            raise TypeError("div requires BigNum128")
        if other.value == 0:
            raise ZeroDivisionError("BigNum128 division by zero")
        # Fixed-point division: (a * SCALE) // b
        new_val = (self.value * self.SCALE) // other.value
        if new_val > self.MAX_VALUE:
            raise OverflowError("BigNum128 division overflow")
        return BigNum128(new_val)

    # ------------------------------
    # Serialization for PQC
    # ------------------------------
    def serialize_for_sign(self) -> bytes:
        """Returns deterministic bytes for PQC signing."""
        return self.to_decimal_string().encode('utf-8')