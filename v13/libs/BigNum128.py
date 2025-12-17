"""
BigNum128.py - Unsigned Fixed-Point Number Class for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready, Fully Auditable
"""

import json
from typing import Any, Dict, List, Union

# Custom exception for BigNum128 operations
class BigNum128Error(Exception):
    """Custom exception for BigNum128 operations."""
    pass

# Remove circular import - CertifiedMath will be imported when needed
# from .CertifiedMath import CertifiedMath

class BigNum128:
    """
    Unsigned Fixed-Point number class with 128-bit integer representation and 18 decimal places of precision.
    SCALE = 10^18. Values range from MIN_VALUE (0) to MAX_VALUE (2^128 - 1).
    """
    # Class constants
    SCALE = 1000000000000000000  # 10^18
    SCALE_DIGITS = 18
    MAX_VALUE = 340282366920938463463374607431768211455  # 2^128 - 1
    MIN_VALUE = 0  # Unsigned type

    # Use CertifiedMath for safe arithmetic operations - defer import
    cm = None

    def __init__(self, value: int):
        # Initialize CertifiedMath if not already done
        self._ensure_cm_initialized()
        
        if not isinstance(value, int):
            raise TypeError("BigNum128 only accepts integers")
        if value < self.MIN_VALUE or value > self.MAX_VALUE:
            raise OverflowError(
                f"BigNum128 value {value} out of bounds [{self.MIN_VALUE}, {self.MAX_VALUE}]"
            )
        self.value = value

    def _ensure_cm_initialized(self):
        """Ensure that CertifiedMath is initialized."""
        if self.cm is None:
            from .CertifiedMath import CertifiedMath
            self.cm = CertifiedMath()
            
    @classmethod
    def from_int(cls, integer_val: int):
        """Creates a BigNum128 from a standard Python integer."""
        # Direct multiplication without using CertifiedMath for simple scaling
        scaled_value = integer_val * cls.SCALE
        if scaled_value > cls.MAX_VALUE:
            raise OverflowError("Integer value too large for BigNum128 after scaling")
        return cls(scaled_value)

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
            
            from .CertifiedMath import CertifiedMath
            cm = CertifiedMath()
            
            # Check integer part overflow BEFORE scaling
            if int(integer_part) > cm.idiv(cls.MAX_VALUE, cls.SCALE):
                raise OverflowError("Integer part too large for BigNum128")
            
            # Deterministic rounding (round half-up) for extra fractional digits
            if len(decimal_part) > cls.SCALE_DIGITS:
                # Check for underflow - if decimal part has more digits than SCALE_DIGITS and the extra digits are non-zero
                extra_digits = decimal_part[cls.SCALE_DIGITS:].rstrip('0')
                if extra_digits:
                    raise BigNum128Error("Input value too small for BigNum128 (underflow)")
                
                # Implement round-half-up for deterministic rounding
                round_digit = int(decimal_part[cls.SCALE_DIGITS]) if len(decimal_part) > cls.SCALE_DIGITS else 0
                # Take the digits up to SCALE_DIGITS
                decimal_part_scaled = decimal_part[:cls.SCALE_DIGITS]
                # Round half-up: if the next digit is >= 5, increment the scaled part
                if round_digit >= 5:
                    decimal_value = cm.add(int(decimal_part_scaled), 1)
                    # Handle overflow from rounding
                    if decimal_value >= cm.pow(10, cls.SCALE_DIGITS):
                        integer_part = str(cm.add(int(integer_part), 1))
                        # Check if incrementing integer_part now exceeds MAX_VALUE // SCALE
                        if int(integer_part) > cm.idiv(cls.MAX_VALUE, cls.SCALE):
                            raise OverflowError("Integer part overflow after rounding")
                        decimal_part_scaled = '0' * cls.SCALE_DIGITS
                    else:
                        decimal_part_scaled = str(decimal_value).zfill(cls.SCALE_DIGITS)
                else:
                    decimal_part_scaled = decimal_part_scaled.ljust(cls.SCALE_DIGITS, '0')
            else:
                # Pad with zeros if fewer digits than SCALE_DIGITS
                decimal_part_scaled = decimal_part.ljust(cls.SCALE_DIGITS, '0')
            
            # Use direct integer arithmetic for the final calculation to avoid BigNum128 objects
            value = int(integer_part) * cls.SCALE + int(decimal_part_scaled)
    
        else:  # Integer string
            if not s.isdigit():
                raise ValueError("Input string must contain only digits")
            
            from .CertifiedMath import CertifiedMath
            cm = CertifiedMath()
            if int(s) > cm.idiv(cls.MAX_VALUE, cls.SCALE):
                raise OverflowError("Integer value too large for BigNum128")
            
            # Use direct integer arithmetic for the final calculation to avoid BigNum128 objects
            value = int(s) * cls.SCALE
        
        if value > cls.MAX_VALUE:
            raise OverflowError("Scaled value exceeds BigNum128 capacity")
        
        return cls(value)

    def to_decimal_string(self, fixed_width: bool = False) -> str:
        """Converts the internal integer value to its fixed-point decimal string representation.
        
        Args:
            fixed_width: If True, always output 18 fractional digits for full auditability.
                        If False, strip trailing zeros (default behavior).
        """
        raw_str = str(self.value).zfill(self.SCALE_DIGITS + 1)
        integer_part = raw_str[:-self.SCALE_DIGITS] or "0"
        if fixed_width:
            # Always output SCALE_DIGITS fractional digits for auditability
            fractional_part = raw_str[-self.SCALE_DIGITS:]
        else:
            # Strip trailing zeros (default behavior)
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
            return False
        return self.value < other.value

    def __le__(self, other):
        if not isinstance(other, BigNum128):
            return False
        return self.value <= other.value

    def __gt__(self, other):
        if not isinstance(other, BigNum128):
            return False
        return self.value > other.value

    def __ge__(self, other):
        if not isinstance(other, BigNum128):
            return False
        return self.value >= other.value

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.value)

    # Arithmetic operator overloads for syntactic sugar
    def __add__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.sub(other)

    def __mul__(self, other):
        return self.mul(other)

    def __truediv__(self, other):
        return self.div(other)

    def __floordiv__(self, other):
        return self.div(other)

    def __mod__(self, other):
        if not isinstance(other, BigNum128):
            raise TypeError("mod requires BigNum128")
        from .CertifiedMath import CertifiedMath
        cm = CertifiedMath()
        return BigNum128(cm.mod(self.value, other.value))

    # Utility methods
    def copy(self) -> 'BigNum128':
        """Returns a copy of this BigNum128 instance."""
        return BigNum128(self.value)

    # Zero/One constants (for convenience in HSMF logic)
    @classmethod
    def zero(cls):
        return cls(0)

    @classmethod
    def one(cls):
        from .CertifiedMath import CertifiedMath
        cm = CertifiedMath()
        return cls(cm.mul(1, cls.SCALE))

    # ------------------------------
    # Arithmetic Operations
    # ------------------------------
    def add(self, other: 'BigNum128') -> 'BigNum128':
        """Adds two BigNum128 values."""
        from .CertifiedMath import CertifiedMath
        cm = CertifiedMath()
        result = cm.add(self.value, other.value)
        if result > self.MAX_VALUE:
            raise OverflowError("Addition result exceeds BigNum128 capacity")
        return BigNum128(result)

    def sub(self, other: 'BigNum128') -> 'BigNum128':
        """Subtracts two BigNum128 values."""
        from .CertifiedMath import CertifiedMath
        cm = CertifiedMath()
        if self.value < other.value:
            raise OverflowError("Subtraction result would be negative (unsigned type)")
        result = cm.sub(self.value, other.value)
        return BigNum128(result)

    def mul(self, other: 'BigNum128') -> 'BigNum128':
        """Multiplies two BigNum128 values."""
        from .CertifiedMath import CertifiedMath
        cm = CertifiedMath()
        # Perform multiplication with proper scaling
        result = cm.mul(self.value, other.value)
        # Divide by scale to maintain fixed-point precision
        result = cm.idiv(result, self.SCALE)
        if result > self.MAX_VALUE:
            raise OverflowError("Multiplication result exceeds BigNum128 capacity")
        return BigNum128(result)

    def div(self, other: 'BigNum128') -> 'BigNum128':
        """Divides two BigNum128 values."""
        if other.value == 0:
            raise ZeroDivisionError("Division by zero")
        from .CertifiedMath import CertifiedMath
        cm = CertifiedMath()
        # Perform division with proper scaling
        # Multiply by scale to maintain fixed-point precision
        result = cm.mul(self.value, self.SCALE)
        result = cm.idiv(result, other.value)
        return BigNum128(result)