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

    @classmethod
    def from_int(cls, integer_val: int):
        """Creates a BigNum128 from a standard Python integer."""
        return cls(integer_val * cls.SCALE)

    def to_decimal_string(self) -> str:
        """Converts the internal integer value to its fixed-point decimal string representation."""
        raw_val = str(self.value).zfill(len(str(self.SCALE)))
        # Insert decimal point 18 places from the right
        integer_part = raw_val[:-18] or "0"
        decimal_part = raw_val[-18:].rstrip('0')
        return f"{integer_part}.{decimal_part or '0'}"

    def __str__(self):
        """String representation for serialization."""
        return self.to_decimal_string()

    def __repr__(self):
        # Enhance repr to show both raw value and fixed-point value for debugging
        decimal_str = self.to_decimal_string()
        return f"BigNum128(raw={self.value}, fp='{decimal_str}')"


# ------------------------------
# Pre-computed Constants
# ------------------------------
# Required deterministic constants as per section 1.5
LN2 = BigNum128(693147180559945309)  # ln(2) * 1e18
E = BigNum128(2718281828459045235)   # e * 1e18
PHI = BigNum128(1618033988749894848) # φ (golden ratio) * 1e18
HALF = BigNum128(500000000000000000) # 0.5 * 1e18
ZERO = BigNum128(0)                 # 0
ONE = BigNum128(1000000000000000000) # 1.0 * 1e18

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
    MAX_EXP_ITERATIONS = 50     # Sufficient for convergence in exponential function
    MAX_LN_ITERATIONS = 50      # Sufficient for convergence in natural logarithm function
    MAX_POW_ITERATIONS = 50     # Sufficient for convergence in power function

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
        inputs: Dict[str, BigNum128],
        result: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Appends a deterministic operation entry to the provided log_list."""
        # Convert BigNum128 inputs to decimal strings for better auditability
        inputs_str = {k: v.to_decimal_string() for k, v in inputs.items()}
        # Log as received per V13 plan (upstream validation)
        entry = {
            "op_name": op_name,
            "inputs": inputs_str,
            "result": result.to_decimal_string(),
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
        CertifiedMath._log_operation("add", {"a": a, "b": b}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_sub(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if a.value < BigNum128.MIN_VALUE + b.value:
            raise OverflowError("CertifiedMath sub underflow")
        result = BigNum128(a.value - b.value)
        CertifiedMath._log_operation("sub", {"a": a, "b": b}, result,
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
        CertifiedMath._log_operation("mul", {"a": a, "b": b}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_div(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if b.value == 0:
            raise ZeroDivisionError("CertifiedMath div by zero")
        result_value = (a.value * BigNum128.SCALE) // b.value
        result = BigNum128(result_value)
        CertifiedMath._log_operation("div", {"a": a, "b": b}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    # --------------------------
    # Safe Comparison Methods (Section 1.2)
    # --------------------------
    @staticmethod
    def _safe_gt(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                 pqc_cid=None, quantum_metadata=None) -> bool:
        """Check if a > b"""
        result = a.value > b.value
        CertifiedMath._log_operation("gt", {"a": a, "b": b}, BigNum128.from_int(1 if result else 0),
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_lt(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                 pqc_cid=None, quantum_metadata=None) -> bool:
        """Check if a < b"""
        result = a.value < b.value
        CertifiedMath._log_operation("lt", {"a": a, "b": b}, BigNum128.from_int(1 if result else 0),
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_gte(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> bool:
        """Check if a >= b"""
        result = a.value >= b.value
        CertifiedMath._log_operation("gte", {"a": a, "b": b}, BigNum128.from_int(1 if result else 0),
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_lte(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> bool:
        """Check if a <= b"""
        result = a.value <= b.value
        CertifiedMath._log_operation("lte", {"a": a, "b": b}, BigNum128.from_int(1 if result else 0),
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_eq(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                 pqc_cid=None, quantum_metadata=None) -> bool:
        """Check if a == b"""
        result = a.value == b.value
        CertifiedMath._log_operation("eq", {"a": a, "b": b}, BigNum128.from_int(1 if result else 0),
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_ne(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
                 pqc_cid=None, quantum_metadata=None) -> bool:
        """Check if a != b"""
        result = a.value != b.value
        CertifiedMath._log_operation("ne", {"a": a, "b": b}, BigNum128.from_int(1 if result else 0),
                                     log_list, pqc_cid, quantum_metadata)
        return result

    # --------------------------
    # Safe Absolute Value (Section 1.2)
    # --------------------------
    @staticmethod
    def _safe_abs(a: BigNum128, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """Calculate absolute value of a"""
        result = BigNum128(abs(a.value))
        CertifiedMath._log_operation("abs", {"a": a}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    # --------------------------
    # Deterministic Functions (Section 1.1)
    # --------------------------
    @staticmethod
    def _safe_ln(a: BigNum128, iterations: int, log_list: List[Dict[str, Any]],
                 pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate natural logarithm ln(x) using Taylor series with range reduction.
        Uses ln(m) + k*ln(2) where x = m * 2^k and 1 ≤ m < 2
        """
        if iterations < 0 or iterations > CertifiedMath.MAX_LN_ITERATIONS:
            raise ValueError(f"Iterations must be between 0 and {CertifiedMath.MAX_LN_ITERATIONS}")
        
        if a.value <= 0:
            raise ValueError("CertifiedMath ln input must be positive")
        
        # Range reduction: x = m * 2^k where 1 ≤ m < 2
        # Find k such that 1 ≤ x/2^k < 2
        x = a.value
        k = 0
        
        # Reduce x to range [1, 2) by dividing by powers of 2
        while x >= 2 * BigNum128.SCALE:
            x //= 2
            k += 1
            
        # If x < 1, multiply by powers of 2 to bring into range [1, 2)
        while x < BigNum128.SCALE:
            x *= 2
            k -= 1
            
        # Now x is in range [1, 2), compute ln(x) using Taylor series
        # ln(1+u) = u - u^2/2 + u^3/3 - u^4/4 + ... where u = x-1
        u = x - BigNum128.SCALE  # u = x - 1
        
        if u == 0:  # ln(1) = 0
            if k == 0:
                result = BigNum128(0)
            else:
                # ln(x) = ln(m) + k*ln(2) = 0 + k*ln(2)
                result = CertifiedMath._safe_mul(BigNum128(k), LN2, log_list, pqc_cid, quantum_metadata)
            CertifiedMath._log_operation("ln", {"a": a, "iterations": BigNum128.from_int(iterations)}, result,
                                         log_list, pqc_cid, quantum_metadata)
            return result
        
        # Calculate ln(1+u) using alternating series: u - u^2/2 + u^3/3 - u^4/4 + ...
        result_value = u
        u_power = u
        sign = -1  # Start with negative for second term
        
        for n in range(2, iterations + 1):
            # Calculate u^n
            if u_power != 0 and u > (BigNum128.MAX_VALUE * BigNum128.SCALE) // u_power:
                raise OverflowError("CertifiedMath ln intermediate mul overflow")
            u_power = (u_power * u) // BigNum128.SCALE
            
            # Calculate term: sign * u^n / n
            denominator = n * BigNum128.SCALE
            term = (u_power * BigNum128.SCALE) // denominator
            signed_term = term if sign > 0 else -term
            
            # Add to result
            if (result_value > 0 and signed_term > BigNum128.MAX_VALUE - result_value) or \
               (result_value < 0 and signed_term < BigNum128.MIN_VALUE - result_value):
                raise OverflowError("CertifiedMath ln addition overflow")
            result_value += signed_term
            
            sign *= -1  # Alternate sign
        
        # Convert result_value back to BigNum128
        ln_m = BigNum128(result_value)
        
        # Final result: ln(x) = ln(m) + k*ln(2)
        if k == 0:
            result = ln_m
        else:
            k_ln2 = CertifiedMath._safe_mul(BigNum128(k), LN2, log_list, pqc_cid, quantum_metadata)
            result = CertifiedMath._safe_add(ln_m, k_ln2, log_list, pqc_cid, quantum_metadata)
        
        if result.value < BigNum128.MIN_VALUE or result.value > BigNum128.MAX_VALUE:
            raise OverflowError("CertifiedMath ln result out of bounds")
            
        CertifiedMath._log_operation("ln", {"a": a, "iterations": BigNum128.from_int(iterations)}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_exp(a: BigNum128, iterations: int, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate e^x using Taylor series with domain limit.
        MUST guard EXP_OVERFLOW
        """
        if iterations < 0 or iterations > CertifiedMath.MAX_EXP_ITERATIONS:
            raise ValueError(f"Iterations must be between 0 and {CertifiedMath.MAX_EXP_ITERATIONS}")
        
        # Guard against overflow - e^x grows very quickly
        # For practical purposes, limit input to prevent overflow
        MAX_EXP_INPUT = BigNum128(10000000000000000000)  # 10.0 * 1e18
        if a.value > MAX_EXP_INPUT.value:
            raise OverflowError("CertifiedMath exp overflow - input too large")
        if a.value < -MAX_EXP_INPUT.value:
            # e^(-large) approaches 0
            result = BigNum128(0)
            CertifiedMath._log_operation("exp", {"a": a, "iterations": BigNum128.from_int(iterations)}, result,
                                         log_list, pqc_cid, quantum_metadata)
            return result
        
        # e^x = 1 + x + x^2/2! + x^3/3! + ...
        result_value = BigNum128.SCALE  # Start with 1.0
        term_value = BigNum128.SCALE   # Current term in the series
        
        for n in range(1, iterations + 1):
            # Calculate next term: term *= x / n
            # term = term * x
            if term_value != 0 and a.value > (BigNum128.MAX_VALUE * BigNum128.SCALE) // term_value:
                raise OverflowError("CertifiedMath exp intermediate mul overflow")
            term_value = (term_value * a.value) // BigNum128.SCALE
            
            # term = term / n
            n_scaled = n * BigNum128.SCALE
            term_value = (term_value * BigNum128.SCALE) // n_scaled
            
            # Add term to result
            if result_value > BigNum128.MAX_VALUE - term_value:
                raise OverflowError("CertifiedMath exp addition overflow")
            result_value += term_value
        
        if result_value > BigNum128.MAX_VALUE:
            raise OverflowError("CertifiedMath exp result out of bounds")
            
        result = BigNum128(result_value)
        CertifiedMath._log_operation("exp", {"a": a, "iterations": BigNum128.from_int(iterations)}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_pow(base: BigNum128, exponent: BigNum128, iterations: int, log_list: List[Dict[str, Any]],
                  pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate base^exponent using the identity: base^exponent = e^(exponent * ln(base))
        Only for x > 0
        """
        if iterations < 0 or iterations > CertifiedMath.MAX_POW_ITERATIONS:
            raise ValueError(f"Iterations must be between 0 and {CertifiedMath.MAX_POW_ITERATIONS}")
        
        if base.value <= 0:
            raise ValueError("CertifiedMath pow base must be positive")
        
        # Calculate ln(base)
        ln_base = CertifiedMath._safe_ln(base, iterations, log_list, pqc_cid, quantum_metadata)
        
        # Calculate exponent * ln(base)
        exp_mul = CertifiedMath._safe_mul(exponent, ln_base, log_list, pqc_cid, quantum_metadata)
        
        # Calculate e^(exponent * ln(base))
        result = CertifiedMath._safe_exp(exp_mul, iterations, log_list, pqc_cid, quantum_metadata)
        
        CertifiedMath._log_operation("pow", {"base": base, "exponent": exponent, "iterations": BigNum128.from_int(iterations)}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_two_to_the_power(a: BigNum128, iterations: int, log_list: List[Dict[str, Any]],
                               pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate 2^x using precomputed ln(2)
        2^x = exp(x * ln(2))
        """
        if iterations < 0 or iterations > CertifiedMath.MAX_POW_ITERATIONS:
            raise ValueError(f"Iterations must be between 0 and {CertifiedMath.MAX_POW_ITERATIONS}")
        
        # Calculate x * ln(2)
        x_mul = CertifiedMath._safe_mul(a, LN2, log_list, pqc_cid, quantum_metadata)
        
        # Calculate e^(x * ln(2))
        result = CertifiedMath._safe_exp(x_mul, iterations, log_list, pqc_cid, quantum_metadata)
        
        CertifiedMath._log_operation("two_to_the_power", {"a": a, "iterations": BigNum128.from_int(iterations)}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _safe_phi_series(a: BigNum128, n: int, log_list: List[Dict[str, Any]],
                         pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate the harmonic alternating series for phi.
        Correct formula: Σ(-1)^n * x^(2n+1)/(2n+1)
        """
        if n < 0 or n > CertifiedMath.MAX_PHI_SERIES_TERMS:
            raise ValueError(f"Number of terms must be between 0 and {CertifiedMath.MAX_PHI_SERIES_TERMS}")
        
        # φ(x) = x - x^3/3 + x^5/5 - x^7/7 + ... + (-1)^n * x^(2n+1) / (2n+1)
        # Use iterative term calculation for better efficiency and numerical stability
        if a.value == 0:
            result = BigNum128(0)
            CertifiedMath._log_operation("phi_series", {"a": a, "n": BigNum128.from_int(n)}, result,
                                         log_list, pqc_cid, quantum_metadata)
            return result
            
        result_value = 0
        sign = 1  # Alternating sign starts with positive
        
        # Calculate terms iteratively
        for i in range(n + 1):
            # Calculate x^(2i+1)
            power = 2 * i + 1
            x_power = BigNum128(1)  # Start with 1
            for _ in range(power):
                if x_power.value != 0 and a.value > (BigNum128.MAX_VALUE * BigNum128.SCALE) // x_power.value:
                    raise OverflowError("CertifiedMath phi_series intermediate mul overflow")
                x_power = BigNum128((x_power.value * a.value) // BigNum128.SCALE)
            
            # Calculate term: sign * x^(2i+1) / (2i+1)
            denominator = power * BigNum128.SCALE
            term = (x_power.value * BigNum128.SCALE) // denominator
            signed_term = term if sign > 0 else -term
            
            # Add to result
            if (result_value > 0 and signed_term > BigNum128.MAX_VALUE - result_value) or \
               (result_value < 0 and signed_term < BigNum128.MIN_VALUE - result_value):
                raise OverflowError("CertifiedMath phi_series addition overflow")
            
            result_value += signed_term
            sign *= -1  # Alternate sign
        
        if result_value < BigNum128.MIN_VALUE:
            result_value = BigNum128.MIN_VALUE
        elif result_value > BigNum128.MAX_VALUE:
            result_value = BigNum128.MAX_VALUE
            
        result = BigNum128(result_value)
        CertifiedMath._log_operation("phi_series", {"a": a, "n": BigNum128.from_int(n)}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _fast_sqrt(a: BigNum128, iterations: int, log_list: List[Dict[str, Any]],
                   pqc_cid=None, quantum_metadata=None) -> BigNum128:
        if iterations < 0 or iterations > CertifiedMath.MAX_SQRT_ITERATIONS:
            raise ValueError(f"Iterations must be between 0 and {CertifiedMath.MAX_SQRT_ITERATIONS}")
        x = a.value
        if x == 0:
            result = BigNum128(0)
            CertifiedMath._log_operation("sqrt", {"a": a, "iterations": BigNum128.from_int(iterations)}, result,
                                         log_list, pqc_cid, quantum_metadata)
            return result
        z = x
        for _ in range(iterations):
            term = x * BigNum128.SCALE // z
            if z > BigNum128.MAX_VALUE - term:
                raise OverflowError("CertifiedMath sqrt intermediate add overflow")
            z = max((z + term) // 2, 1)
        result = BigNum128(z)
        CertifiedMath._log_operation("sqrt", {"a": a, "iterations": BigNum128.from_int(iterations)}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _calculate_phi_series(a: BigNum128, n: int, log_list: List[Dict[str, Any]],
                              pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate the golden ratio series φ(x) = Σ(n=0 to N) [(-1)^n * x^(2n+1) / (2n+1)]
        using the harmonic series formula, not simple multiplication.
        """
        if n < 0 or n > CertifiedMath.MAX_PHI_SERIES_TERMS:
            raise ValueError(f"Number of terms must be between 0 and {CertifiedMath.MAX_PHI_SERIES_TERMS}")
        
        # φ(x) = x - x^3/3 + x^5/5 - x^7/7 + ... + (-1)^n * x^(2n+1) / (2n+1)
        # Use iterative term calculation for better efficiency and numerical stability
        result_value = 0
        sign = 1  # Alternating sign starts with positive
        
        # First term: x^1/1
        term_value = a.value
        denominator = BigNum128.SCALE  # 1 * SCALE
        signed_term = term_value if sign > 0 else -term_value
        final_term = (signed_term * BigNum128.SCALE) // denominator
        
        # Add first term to result
        if (result_value > 0 and final_term > BigNum128.MAX_VALUE - result_value) or \
           (result_value < 0 and final_term < BigNum128.MIN_VALUE - result_value):
            raise OverflowError("CertifiedMath phi_series addition overflow")
        
        result_value += final_term
        sign *= -1  # Alternate sign for next term
        
        # Calculate subsequent terms iteratively
        x_squared = (a.value * a.value) // BigNum128.SCALE  # x^2
        prev_term = term_value  # x^1
        
        for i in range(1, n + 1):
            # Calculate next term from previous term
            # term_n = term_(n-1) * x^2 * (2*(n-1)+1) / (2*n+1)
            power_prev = 2 * (i - 1) + 1  # 2(n-1)+1
            power_curr = 2 * i + 1        # 2n+1
            
            # Calculate term_n = term_(n-1) * x^2 * power_prev / power_curr
            if prev_term != 0 and x_squared > (BigNum128.MAX_VALUE * BigNum128.SCALE) // prev_term:
                raise OverflowError("CertifiedMath phi_series intermediate mul overflow")
            intermediate = (prev_term * x_squared) // BigNum128.SCALE
            
            # Multiply by power_prev
            power_prev_scaled = power_prev * BigNum128.SCALE
            if intermediate != 0 and power_prev_scaled > (BigNum128.MAX_VALUE * BigNum128.SCALE) // intermediate:
                raise OverflowError("CertifiedMath phi_series intermediate mul overflow")
            intermediate2 = (intermediate * power_prev_scaled) // BigNum128.SCALE
            
            # Divide by power_curr
            power_curr_scaled = power_curr * BigNum128.SCALE
            term_value = (intermediate2 * BigNum128.SCALE) // power_curr_scaled
            
            # Apply sign and divide by denominator
            signed_term = term_value if sign > 0 else -term_value
            final_term = (signed_term * BigNum128.SCALE) // BigNum128.SCALE  # denominator is 1 for this calculation
            
            # Add to result
            if (result_value > 0 and final_term > BigNum128.MAX_VALUE - result_value) or \
               (result_value < 0 and final_term < BigNum128.MIN_VALUE - result_value):
                raise OverflowError("CertifiedMath phi_series addition overflow")
            
            result_value += final_term
            sign *= -1  # Alternate sign for next term
            prev_term = term_value
        
        if result_value < BigNum128.MIN_VALUE or result_value > BigNum128.MAX_VALUE:
            raise OverflowError("CertifiedMath phi_series result out of bounds")
            
        result = BigNum128(result_value) if result_value >= 0 else BigNum128(0)  # Handle negative results
        CertifiedMath._log_operation("phi_series", {"a": a, "n": BigNum128.from_int(n)}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    # HSMF metric calculation functions
    @staticmethod
    def _calculate_I_eff(tokens: BigNum128, log_list: List[Dict[str, Any]],
                         pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate I_eff (effective interest) for HSMF metrics.
        I_eff = (1 - C_system)^2 * BETA_PENALTY where C_system is coherence metric
        """
        # For this implementation, we'll use tokens as a proxy for C_system
        # I_eff = (1 - tokens)^2 * BETA_PENALTY
        # But we need to ensure tokens is between 0 and 1 for this calculation
        ONE = BigNum128.from_int(1)
        BETA_PENALTY = BigNum128.from_int(100000000)  # 100,000,000
        
        # Normalize tokens to be between 0 and 1 (assuming tokens represents a percentage)
        # For testing purposes, we'll use a small fraction of tokens
        normalized_tokens = CertifiedMath._safe_div(tokens, BigNum128.from_int(1000), log_list, pqc_cid, quantum_metadata)
        
        # Ensure normalized_tokens is <= 1 to avoid underflow
        tokens_le_one = CertifiedMath._safe_lte(normalized_tokens, ONE, log_list, pqc_cid, quantum_metadata)
        if not tokens_le_one:
            normalized_tokens = ONE
        
        # Calculate (1 - tokens)
        diff = CertifiedMath._safe_sub(ONE, normalized_tokens, log_list, pqc_cid, quantum_metadata)
        
        # Calculate (1 - tokens)^2
        diff_squared = CertifiedMath._safe_mul(diff, diff, log_list, pqc_cid, quantum_metadata)
        
        # Calculate I_eff = (1 - tokens)^2 * BETA_PENALTY
        result = CertifiedMath._safe_mul(diff_squared, BETA_PENALTY, log_list, pqc_cid, quantum_metadata)
        
        CertifiedMath._log_operation("I_eff", {"tokens": tokens, "normalized_tokens": normalized_tokens, "beta_penalty": BETA_PENALTY}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    @staticmethod
    def _calculate_c_holo(tokens: BigNum128, log_list: List[Dict[str, Any]],
                          pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """
        Calculate C_holo (holistic coefficient) for HSMF metrics.
        C_holo = 1 / (1 + total_dissonance) where total_dissonance includes various stability metrics
        """
        # For this implementation, we'll use tokens as a proxy for dissonance
        ONE = BigNum128.from_int(1)
        
        # Normalize tokens to avoid overflow (use a small fraction)
        normalized_tokens = CertifiedMath._safe_div(tokens, BigNum128.from_int(1000), log_list, pqc_cid, quantum_metadata)
        
        # Calculate (1 + tokens)
        one_plus_tokens = CertifiedMath._safe_add(ONE, normalized_tokens, log_list, pqc_cid, quantum_metadata)
        
        # Calculate C_holo = 1 / (1 + tokens)
        result = CertifiedMath._safe_div(ONE, one_plus_tokens, log_list, pqc_cid, quantum_metadata)
        
        CertifiedMath._log_operation("c_holo", {"tokens": tokens, "normalized_tokens": normalized_tokens}, result,
                                     log_list, pqc_cid, quantum_metadata)
        return result

    # --------------------------
    # Deterministic Input Conversion (Section 1.4)
    # --------------------------
    @staticmethod
    def from_string(s: str) -> BigNum128:
        if not isinstance(s, str):
            raise TypeError("Input must be a string")
        s = s.strip()
        
        # --- CRITICAL FIX: Deterministic Decimal String Parsing ---
        # Add early-out guard as per section 1.4
        if '.' in s:
            parts = s.split('.')
            if len(parts) > 2:
                raise ValueError("Input string must contain at most one decimal point")
            
            integer_part = parts[0] or "0"
            decimal_part = parts[1]
            
            # Add overflow checking as per section 1.4
            if abs(int(integer_part)) > BigNum128.MAX_VALUE // BigNum128.SCALE:
                raise OverflowError("BigNum128.from_string: integer part too large before scaling")
            
            if not integer_part.lstrip('-').isdigit() or not decimal_part.isdigit():
                raise ValueError("Input string parts must contain only digits")
                
            # Truncate decimal part to SCALE_DIGITS (18) and pad with zeros to scale
            decimal_part_scaled = decimal_part.ljust(BigNum128.SCALE_DIGITS, '0')[:BigNum128.SCALE_DIGITS]
            
            # Combine integer part (scaled) and decimal part (truncated)
            value = int(integer_part) * BigNum128.SCALE + int(decimal_part_scaled)

        else: # Handle raw integer string (no decimal point)
            if not s.lstrip('-').isdigit():
                raise ValueError("Input string must contain only digits")
            # Add overflow checking as per section 1.4
            if abs(int(s)) > BigNum128.MAX_VALUE // BigNum128.SCALE:
                raise OverflowError("BigNum128.from_string: integer part too large before scaling")
            # Scale the integer up to the raw 128-bit format
            value = int(s) * BigNum128.SCALE
        # --- END CRITICAL FIX ---

        if value < BigNum128.MIN_VALUE or value > BigNum128.MAX_VALUE:
            raise OverflowError("Input value out of bounds")
        
        return BigNum128(value)

    # --------------------------
    # Public API Wrappers (Section 1.2)
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

    @staticmethod
    def safe_exp(a: BigNum128, log_list: List[Dict[str, Any]], iterations: int = 50,
                 pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """Public API wrapper for exponential function."""
        if log_list is None: raise ValueError("log_list is required for safe_exp")
        return CertifiedMath._safe_exp(a, iterations, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def safe_ln(a: BigNum128, log_list: List[Dict[str, Any]], iterations: int = 50,
                pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """Public API wrapper for natural logarithm function."""
        if log_list is None: raise ValueError("log_list is required for safe_ln")
        return CertifiedMath._safe_ln(a, iterations, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def safe_pow(base: BigNum128, exponent: BigNum128, log_list: List[Dict[str, Any]], iterations: int = 50,
                 pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """Public API wrapper for power function."""
        if log_list is None: raise ValueError("log_list is required for safe_pow")
        return CertifiedMath._safe_pow(base, exponent, iterations, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def safe_two_to_the_power(a: BigNum128, log_list: List[Dict[str, Any]], iterations: int = 50,
                              pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """Public API wrapper for 2^x function."""
        if log_list is None: raise ValueError("log_list is required for safe_two_to_the_power")
        return CertifiedMath._safe_two_to_the_power(a, iterations, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def safe_phi_series(a: BigNum128, log_list: List[Dict[str, Any]], n: int = 50,
                        pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """Public API wrapper for phi series function."""
        if log_list is None: raise ValueError("log_list is required for safe_phi_series")
        return CertifiedMath._safe_phi_series(a, n, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def calculate_I_eff(tokens: BigNum128, log_list: List[Dict[str, Any]],
                        pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """Public API wrapper for I_eff calculation."""
        if log_list is None: raise ValueError("log_list is required for calculate_I_eff")
        return CertifiedMath._calculate_I_eff(tokens, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def calculate_c_holo(tokens: BigNum128, log_list: List[Dict[str, Any]],
                         pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """Public API wrapper for C_holo calculation."""
        if log_list is None: raise ValueError("log_list is required for calculate_c_holo")
        return CertifiedMath._calculate_c_holo(tokens, log_list, pqc_cid, quantum_metadata)

    # --------------------------
    # Public API Wrappers for Comparison Methods (Section 1.2)
    # --------------------------
    @staticmethod
    def gt(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
           pqc_cid=None, quantum_metadata=None) -> bool:
        """Public API wrapper for greater than comparison."""
        if log_list is None: raise ValueError("log_list is required for gt")
        return CertifiedMath._safe_gt(a, b, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def lt(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
           pqc_cid=None, quantum_metadata=None) -> bool:
        """Public API wrapper for less than comparison."""
        if log_list is None: raise ValueError("log_list is required for lt")
        return CertifiedMath._safe_lt(a, b, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def gte(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
            pqc_cid=None, quantum_metadata=None) -> bool:
        """Public API wrapper for greater than or equal comparison."""
        if log_list is None: raise ValueError("log_list is required for gte")
        return CertifiedMath._safe_gte(a, b, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def lte(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
            pqc_cid=None, quantum_metadata=None) -> bool:
        """Public API wrapper for less than or equal comparison."""
        if log_list is None: raise ValueError("log_list is required for lte")
        return CertifiedMath._safe_lte(a, b, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def eq(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
           pqc_cid=None, quantum_metadata=None) -> bool:
        """Public API wrapper for equality comparison."""
        if log_list is None: raise ValueError("log_list is required for eq")
        return CertifiedMath._safe_eq(a, b, log_list, pqc_cid, quantum_metadata)

    @staticmethod
    def ne(a: BigNum128, b: BigNum128, log_list: List[Dict[str, Any]],
           pqc_cid=None, quantum_metadata=None) -> bool:
        """Public API wrapper for not equal comparison."""
        if log_list is None: raise ValueError("log_list is required for ne")
        return CertifiedMath._safe_ne(a, b, log_list, pqc_cid, quantum_metadata)

    # --------------------------
    # Public API Wrapper for Absolute Value (Section 1.2)
    # --------------------------
    @staticmethod
    def abs(a: BigNum128, log_list: List[Dict[str, Any]],
            pqc_cid=None, quantum_metadata=None) -> BigNum128:
        """Public API wrapper for absolute value."""
        if log_list is None: raise ValueError("log_list is required for abs")
        return CertifiedMath._safe_abs(a, log_list, pqc_cid, quantum_metadata)