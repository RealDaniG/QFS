"""
CertifiedMath.py: Certified math operations for Zero Simulation Compliance with Fixed-Point Rigor and Quantum Integration
"""
import json
import hashlib
from typing import Any, Tuple, Optional, Dict


class BigNum128:
    """
    Fixed-point number class with 128-bit integer representation and 18 decimal places of precision.
    SCALE = 10^18
    """
    SCALE = 10**18
    MAX_VALUE = 2**128 - 1
    MIN_VALUE = 0

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("BigNum128 only accepts integers")
        if value < self.MIN_VALUE or value > self.MAX_VALUE:
            raise OverflowError(f"BigNum128 value {value} out of bounds [{self.MIN_VALUE}, {self.MAX_VALUE}]")
        self.value = value

    def __repr__(self):
        return f"BigNum128({self.value})"


class CertifiedMath:
    """
    Core deterministic mathematical operations library for QFS V13.
    Enforces Zero-Simulation compliance, fixed-point arithmetic safety,
    and provides atomic logging for auditability.
    """
    _operation_log = [] # Global log for all operations within this process/session

    @staticmethod
    def _log_operation(op_name: str, inputs: Tuple, result: int,
                      pqc_cid: Optional[str] = None,
                      quantum_metadata: Optional[Dict[str, Any]] = None):
        """
        Logs a deterministic operation to the internal log.
        This function is atomic in the sense that it appends one complete dictionary entry.
        CRITICAL: This function should ONLY be called after the operation has been confirmed
        to be mathematically valid (no overflow/underflow/div-by-zero) and the result calculated.
        For Pre-Phase 1: Trusts that quantum_metadata (if present) is already validated by the SDK/API.
        """
        # For Pre-Phase 1: Log the metadata as provided by the SDK/API (or None)
        # The validation of quantum_metadata happens upstream in the SDK/API layer.
        entry = {
            "op_name": op_name,
            "inputs": inputs,
            "result": result,
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata # <-- Use provided metadata directly
        }
        CertifiedMath._operation_log.append(entry)

    @staticmethod
    def get_log_hash() -> str:
        """
        Generates a deterministic SHA-256 hash of the serialized operation log.
        Uses sort_keys=True for consistent ordering and default=str for robust serialization.
        Only includes operations that were successfully logged (i.e., passed all checks).
        """
        # sort_keys ensures deterministic ordering regardless of dict insertion order.
        # default=str prevents serialization errors for future metadata or complex objects,
        # converting them to their string representation deterministically.
        serialized_log = json.dumps(CertifiedMath._operation_log, sort_keys=True, default=str)
        return hashlib.sha256(serialized_log.encode("utf-8")).hexdigest()

    @staticmethod
    def export_log(path: str):
        """
        Export the operation log to a file for persistence.
        
        Args:
            path: Path to the file where the log should be exported
        """
        with open(path, "w") as f:
            # Add default=str for ultimate determinism and consistency
            json.dump(CertifiedMath._operation_log, f, sort_keys=True, default=str)

    # --- Step 2: Safe Arithmetic Methods with Fixed-Point Safety ---

    @staticmethod
    def _safe_add(a: BigNum128, b: BigNum128, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Perform addition with explicit overflow check before calculation and logging.
        
        Check for overflow/underflow before calculation. If check fails, raise OverflowError
        before logging. Otherwise, log after successful calculation.
        """
        # Check for overflow before calculation
        if a.value > BigNum128.MAX_VALUE - b.value:
            raise OverflowError("CertifiedMath add overflow")
        result_value = a.value + b.value
        result = BigNum128(result_value)
        CertifiedMath._log_operation("add", (a.value, b.value), result.value, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_sub(a: BigNum128, b: BigNum128, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Perform subtraction with explicit underflow check before calculation and logging.
        
        Check for overflow/underflow before calculation. If check fails, raise OverflowError
        before logging. Otherwise, log after successful calculation.
        """
        # Check for underflow before calculation
        if a.value < BigNum128.MIN_VALUE + b.value:
            raise OverflowError("CertifiedMath sub underflow")
        result_value = a.value - b.value
        result = BigNum128(result_value)
        CertifiedMath._log_operation("sub", (a.value, b.value), result.value, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_mul(a: BigNum128, b: BigNum128, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Perform multiplication with explicit overflow check before calculation and logging.
        Ensures (a.value * b.value) // SCALE does not overflow BigNum128.MAX_VALUE.
        
        Check for overflow before calculation. If check fails, raise OverflowError
        before logging. Otherwise, log after successful calculation.
        """
        # Check for overflow before calculation
        # Ensure (a.value * b.value) // SCALE <= MAX_VALUE
        # This implies (a.value * b.value) <= MAX_VALUE * SCALE
        # Check: a.value <= (MAX_VALUE * SCALE) // b.value (if b.value != 0)
        if b.value != 0:
            max_product = BigNum128.MAX_VALUE * BigNum128.SCALE
            if a.value > max_product // b.value:
                raise OverflowError("CertifiedMath mul overflow")
        # If b.value is 0, result is 0, no overflow occurs

        result_value = (a.value * b.value) // BigNum128.SCALE
        # Double-check the result is within bounds (should be guaranteed by check above)
        if result_value > BigNum128.MAX_VALUE:
             raise OverflowError("CertifiedMath mul result out of bounds")
        # Optional: Check for underflow (result < MIN_VALUE), though unlikely with non-negative inputs
        # if result_value < BigNum128.MIN_VALUE: # Not strictly necessary if MIN_VALUE is 0
        #     raise OverflowError("CertifiedMath mul result underflow") # Use UnderflowError if defined
        result = BigNum128(result_value)
        CertifiedMath._log_operation("mul", (a.value, b.value), result.value, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_div(a: BigNum128, b: BigNum128, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Perform division with explicit zero division check before calculation and logging.
        
        Check for division by zero before logging. Raise ZeroDivisionError.
        Log after successful calculation.
        """
        if b.value == 0:
            raise ZeroDivisionError("CertifiedMath div by zero")
        result_value = (a.value * BigNum128.SCALE) // b.value
        result = BigNum128(result_value)
        CertifiedMath._log_operation("div", (a.value, b.value), result.value, pqc_cid, quantum_metadata)
        return result

    # --- Step 3: Deterministic Fixed-Point Functions with Fixed Iteration Counts ---

    @staticmethod
    def _fast_sqrt(a: BigNum128, iterations=20, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate square root using Babylonian method with fixed iteration count.
        Includes overflow checks within the loop.
        
        Fixed iterations (e.g., 20) ensure determinism as per V13 Phase 1.
        Log result with iterations count.
        """
        x = a.value
        if x == 0:
            result = BigNum128(0)
            CertifiedMath._log_operation("sqrt", (a.value, iterations), result.value, pqc_cid, quantum_metadata)
            return result

        z = x
        for _ in range(iterations):
            # Check for overflow in intermediate calculations
            # term = x * BigNum128.SCALE // z
            # Check if x * BigNum128.SCALE would overflow (it shouldn't if BigNum128.SCALE is chosen correctly)
            # But check the addition z + term
            term = x * BigNum128.SCALE // z
            if z > BigNum128.MAX_VALUE - term: # Check for overflow in z + term
                raise OverflowError("CertifiedMath sqrt intermediate add overflow")
            next_z_candidate = z + term
            # Check for overflow in (z + term) // 2 (integer division by 2 cannot cause overflow from the add)
            # But check the final result against BigNum128 bounds
            next_z = next_z_candidate // 2
            if next_z > BigNum128.MAX_VALUE: # Should not happen with integer division, but check for safety
                 raise OverflowError("CertifiedMath sqrt result out of bounds")
            z = next_z
            # Ensure z doesn't become zero (could cause issues in next iteration's division)
            z = max(z, 1) # This line is okay, ensures z stays positive

        result = BigNum128(z)
        CertifiedMath._log_operation("sqrt", (a.value, iterations), result.value, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _calculate_phi_series(a: BigNum128, n: int, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate phi series with fixed term count.
        Includes overflow checks within the loop.
        
        Fixed terms count ensures determinism.
        Log result with terms count.
        """
        phi = BigNum128(1618033988749894848)  # fixed-point phi*1e18
        result_value = a.value
        for i in range(n):
            # Check for overflow before calculation: (result_value * phi.value) // SCALE
            # Check if result_value * phi.value would exceed MAX_VALUE * SCALE
            # i.e., result_value > (MAX_VALUE * SCALE) // phi.value (if phi.value != 0)
            if phi.value != 0 and result_value > (BigNum128.MAX_VALUE * BigNum128.SCALE) // phi.value:
                raise OverflowError("CertifiedMath phi_series intermediate mul overflow")
            result_value = (result_value * phi.value) // BigNum128.SCALE
            # Check if the result after division is still within bounds
            if result_value > BigNum128.MAX_VALUE:
                 raise OverflowError("CertifiedMath phi_series result out of bounds")
        result = BigNum128(result_value)
        CertifiedMath._log_operation("phi_series", (a.value, n), result.value, pqc_cid, quantum_metadata)
        return result

    # --- Step 4: Deterministic Input Conversion (Optional Helper) ---

    @staticmethod
    def from_string(s: str) -> BigNum128:
        """
        Convert a string representation of a number to BigNum128.
        Useful for deterministic input parsing.
        """
        if not isinstance(s, str):
            raise TypeError("Input must be a string")
        # Strip whitespace for safety
        s = s.strip()
        if not s.isdigit():
            raise ValueError("Input string must contain only digits")
        value = int(s)
        if value < BigNum128.MIN_VALUE or value > BigNum128.MAX_VALUE:
            raise OverflowError("Input value out of bounds")
        return BigNum128(value)

    # --- Step 5: Public API Wrappers with Exception Propagation ---

    @staticmethod
    def add(a: BigNum128, b: BigNum128, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Public wrapper for addition operation.
        Propagate exceptions (OverflowError, UnderflowError) raised by _safe_add
        """
        return CertifiedMath._safe_add(a, b, pqc_cid, quantum_metadata)

    @staticmethod
    def sub(a: BigNum128, b: BigNum128, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Public wrapper for subtraction operation.
        Propagate exceptions (OverflowError, UnderflowError) raised by _safe_sub
        """
        return CertifiedMath._safe_sub(a, b, pqc_cid, quantum_metadata)

    @staticmethod
    def mul(a: BigNum128, b: BigNum128, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Public wrapper for multiplication operation.
        Propagate exceptions (OverflowError, UnderflowError) raised by _safe_mul
        """
        return CertifiedMath._safe_mul(a, b, pqc_cid, quantum_metadata)

    @staticmethod
    def div(a: BigNum128, b: BigNum128, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Public wrapper for division operation.
        Propagate exceptions (ZeroDivisionError) raised by _safe_div
        """
        return CertifiedMath._safe_div(a, b, pqc_cid, quantum_metadata)

    @staticmethod
    def fast_sqrt(a: BigNum128, iterations: int = 20, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Public wrapper for square root operation.
        Propagate exceptions raised by internal _fast_sqrt
        """
        return CertifiedMath._fast_sqrt(a, iterations, pqc_cid, quantum_metadata)

    @staticmethod
    def calculate_phi_series(a: BigNum128, n: int, pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Public wrapper for phi series operation.
        Propagate exceptions raised by internal _calculate_phi_series
        """
        return CertifiedMath._calculate_phi_series(a, n, pqc_cid, quantum_metadata)
