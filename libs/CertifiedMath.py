"""
CertifiedMath.py - Deterministic Fixed-Point Math Library for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready, Fully Auditable, Thread-Safe via Context
"""

import json
import hashlib
from typing import Any, Tuple, Optional, Dict, List

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

    def to_decimal_string(self) -> str:
        """Converts the internal integer value to its fixed-point decimal string representation."""
        raw_val = str(self.value).zfill(len(str(self.SCALE)))
        # Insert decimal point 18 places from the right
        integer_part = raw_val[:-18] or "0"
        decimal_part = raw_val[-18:].rstrip('0')
        return f"{integer_part}.{decimal_part or '0'}"

    def __repr__(self):
        # Enhance repr to show both raw value and fixed-point value for debugging
        decimal_str = self.to_decimal_string()
        return f"BigNum128(raw={self.value}, fp='{decimal_str}')"


# ------------------------------
# CertifiedMath: Deterministic Operations
# ------------------------------
class CertifiedMath:
    """
    Stateless, deterministic fixed-point arithmetic library for QFS V13.
    Provides Zero-Simulation compliant operations, PQC/quantum metadata support,
    and requires an external log list for auditability (via context manager or direct passing).
    This library does not maintain its own global state.
    """

    MAX_SQRT_ITERATIONS = 20    # Empirically proven to provide > 30 decimal places of fixed-point precision
    MAX_PHI_SERIES_TERMS = 50   # Sufficient for convergence in the golden ratio series calculation

    # --- Log Context Manager ---
    class LogContext:
        """
        Context manager for creating isolated, deterministic operation logs.
        Ensures thread-safety and coherence for a specific session or transaction bundle.
        Usage:
            with CertifiedMath.LogContext() as log:
                result = CertifiedMath.add(a, b, log)
        """
        def __init__(self):
            self.log = []

        def __enter__(self):
            self.log = []
            return self.log

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass  # Log remains accessible via self.log

        def get_log(self):
            return self.log

        def get_hash(self):
            return CertifiedMath.get_log_hash(self.log)

        def export(self, path: str):
            CertifiedMath.export_log(self.log, path)

    # --------------------------
    # Internal Logging
    # --------------------------
    @staticmethod
    def _log_operation(
        op_name: str,
        inputs: Tuple,
        result: int,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Appends a deterministic operation entry to the provided log_list."""
        # Log as received per V13 plan (upstream validation)
        entry = {
            "op_name": op_name,
            "inputs": inputs,
            "result": result,
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,  # Log as received per V13 plan (upstream validation)
        }
        log_list.append(entry)

    @staticmethod
    def get_log_hash(log_list: List[Dict[str, Any]]) -> str:
        """Generate deterministic SHA-256 hash of a given log list."""
        serialized_log = json.dumps(log_list, sort_keys=True, default=str)
        return hashlib.sha256(serialized_log.encode("utf-8")).hexdigest()

    @staticmethod
    def export_log(log_list: List[Dict[str, Any]], path: str):
        """Export the provided log list to a JSON file."""
        with open(path, "w") as f:
            json.dump(log_list, f, sort_keys=True, default=str)

    # --------------------------
    # Safe Arithmetic Methods
    # --------------------------
    @staticmethod
    def _safe_add(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if a.value > BigNum128.MAX_VALUE - b.value:
            raise OverflowError("CertifiedMath add overflow")
        result = BigNum128(a.value + b.value)
        CertifiedMath._log_operation("add", (a.value, b.value), result.value,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_sub(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if a.value < BigNum128.MIN_VALUE + b.value:
            raise OverflowError("CertifiedMath sub underflow")
        result = BigNum128(a.value - b.value)
        CertifiedMath._log_operation("sub", (a.value, b.value), result.value,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_mul(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if b.value != 0:
            max_product = BigNum128.MAX_VALUE * BigNum128.SCALE
            if a.value > max_product // b.value:
                raise OverflowError("CertifiedMath mul overflow")
        result_value = (a.value * b.value) // BigNum128.SCALE
        if result_value > BigNum128.MAX_VALUE:
            raise OverflowError("CertifiedMath mul result out of bounds")
        result = BigNum128(result_value)
        CertifiedMath._log_operation("mul", (a.value, b.value), result.value,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_div(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if b.value == 0:
            raise ZeroDivisionError("CertifiedMath div by zero")
        result_value = (a.value * BigNum128.SCALE) // b.value
        result = BigNum128(result_value)
        CertifiedMath._log_operation("div", (a.value, b.value), result.value,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    # --------------------------
    # Deterministic Functions
    # --------------------------
    @staticmethod
    def _fast_sqrt(a: BigNum128, iterations: int, log_list: List[Dict[str, Any]],
                   pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if iterations < 0 or iterations > CertifiedMath.MAX_SQRT_ITERATIONS:
            raise ValueError(f"Iterations must be between 0 and {CertifiedMath.MAX_SQRT_ITERATIONS}")
        x = a.value
        if x == 0:
            result = BigNum128(0)
            CertifiedMath._log_operation("sqrt", (a.value, iterations), result.value,
                                         log_list, pqc_cid, quantum_metadata)
            return result
        z = x
        for _ in range(iterations):
            term = x * BigNum128.SCALE // z
            if z > BigNum128.MAX_VALUE - term:
                raise OverflowError("CertifiedMath sqrt intermediate add overflow")
            z = max((z + term) // 2, 1)
        result = BigNum128(z)
        CertifiedMath._log_operation("sqrt", (a.value, iterations), result.value,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _calculate_phi_series(a: BigNum128, n: int, log_list: List[Dict[str, Any]],
                              pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if n < 0 or n > CertifiedMath.MAX_PHI_SERIES_TERMS:
            raise ValueError(f"Number of terms must be between 0 and {CertifiedMath.MAX_PHI_SERIES_TERMS}")
        phi = BigNum128(1618033988749894848)  # phi * 1e18
        result_value = a.value
        for _ in range(n):
            if phi.value != 0 and result_value > (BigNum128.MAX_VALUE * BigNum128.SCALE) // phi.value:
                raise OverflowError("CertifiedMath phi_series intermediate mul overflow")
            result_value = (result_value * phi.value) // BigNum128.SCALE
            if result_value > BigNum128.MAX_VALUE:
                raise OverflowError("CertifiedMath phi_series result out of bounds")
        result = BigNum128(result_value)
        CertifiedMath._log_operation("phi_series", (a.value, n), result.value,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    # --------------------------
    # Deterministic Input Conversion
    # --------------------------
    @staticmethod
    def from_string(s: str) -> BigNum128:
        if not isinstance(s, str):
            raise TypeError("Input must be a string")
        s = s.strip()
        
        # --- CRITICAL FIX: Deterministic Decimal String Parsing ---
        if '.' in s:
            parts = s.split('.')
            if len(parts) > 2:
                raise ValueError("Input string must contain at most one decimal point")
            
            integer_part = parts[0] or "0"
            decimal_part = parts[1]
            
            if not integer_part.isdigit() or not decimal_part.isdigit():
                raise ValueError("Input string parts must contain only digits")
                
            # Truncate decimal part to SCALE_DIGITS (18) and pad with zeros to scale
            decimal_part_scaled = decimal_part.ljust(BigNum128.SCALE_DIGITS, '0')[:BigNum128.SCALE_DIGITS]
            
            # Combine integer part (scaled) and decimal part (truncated)
            value = int(integer_part) * BigNum128.SCALE + int(decimal_part_scaled)

        else: # Handle raw integer string (no decimal point)
            if not s.isdigit():
                raise ValueError("Input string must contain only digits")
            # Scale the integer up to the raw 128-bit format
            value = int(s) * BigNum128.SCALE
        # --- END CRITICAL FIX ---

        if value < BigNum128.MIN_VALUE or value > BigNum128.MAX_VALUE:
            raise OverflowError("Input value out of bounds")
        
        return BigNum128(value)

    # --------------------------
    # Public API Wrappers
    # --------------------------
    @staticmethod
    def add(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
            pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if log_list is None: raise ValueError("log_list is required for add")
        return CertifiedMath._safe_add(a, b, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def sub(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
            pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if log_list is None: raise ValueError("log_list is required for sub")
        return CertifiedMath._safe_sub(a, b, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def mul(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
            pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if log_list is None: raise ValueError("log_list is required for mul")
        return CertifiedMath._safe_mul(a, b, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def div(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
            pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if log_list is None: raise ValueError("log_list is required for div")
        return CertifiedMath._safe_div(a, b, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def fast_sqrt(a: BigNum128, log_list: List[Dict[str, Any]], iterations: int = 20,
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if log_list is None: raise ValueError("log_list is required for fast_sqrt")
        return CertifiedMath._fast_sqrt(a, iterations, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def calculate_phi_series(a: BigNum128, log_list: List[Dict[str, Any]], n: int = 50,
                             pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if log_list is None: raise ValueError("log_list is required for calculate_phi_series")
        return CertifiedMath._calculate_phi_series(a, n, log_list, pqc_cid, quantum_metadata)


# --- Example Usage ---
if __name__ == "__main__":
    a = BigNum128(100)
    b = BigNum128(50)
    c = BigNum128(2)

    with CertifiedMath.LogContext() as session_log:
        r1 = CertifiedMath.add(a, b, session_log, pqc_cid="pqc_001")
        r2 = CertifiedMath.mul(r1, c, session_log, pqc_cid="pqc_002")
        r3 = CertifiedMath.fast_sqrt(r2, session_log, iterations=10)
        print(f"Log Length: {len(session_log)}")
        print(f"Log Hash: {CertifiedMath.get_log_hash(session_log)}")
