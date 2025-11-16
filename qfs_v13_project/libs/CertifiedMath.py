"""
CertifiedMath.py: Certified math operations for Zero Simulation Compliance
"""
import json
import hashlib
from typing import Any, Tuple, Optional


class BigNum128:
    SCALE = 10**18
    MAX_VALUE = 2**128 - 1
    MIN_VALUE = 0

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("BigNum128 only accepts integers")
        if value < self.MIN_VALUE or value > self.MAX_VALUE:
            raise OverflowError(f"BigNum128 value {value} out of bounds")
        self.value = value


class CertifiedMath:
    _operation_log = []

    @staticmethod
    def _log_operation(op_name: str, inputs: Tuple, result: int, pqc_cid: Optional[str] = None):
        entry = {
            "op_name": op_name,
            "inputs": inputs,
            "result": result,
            "pqc_cid": pqc_cid
        }
        CertifiedMath._operation_log.append(entry)

    @staticmethod
    def get_log_hash() -> str:
        serialized_log = json.dumps(CertifiedMath._operation_log, sort_keys=True)
        return hashlib.sha256(serialized_log.encode("utf-8")).hexdigest()

    @staticmethod
    def export_log(path: str):
        """
        Export the operation log to a file for persistence.
        
        Args:
            path: Path to the file where the log should be exported
        """
        with open(path, "w") as f:
            json.dump(CertifiedMath._operation_log, f, sort_keys=True)

    # Step 2: Safe Arithmetic Methods
    @staticmethod
    def _safe_add(a: BigNum128, b: BigNum128, pqc_cid=None) -> BigNum128:
        result_value = a.value + b.value
        if result_value > BigNum128.MAX_VALUE:
            raise OverflowError("CertifiedMath add overflow")
        result = BigNum128(result_value)
        CertifiedMath._log_operation("add", (a.value, b.value), result.value, pqc_cid)
        return result

    @staticmethod
    def _safe_sub(a: BigNum128, b: BigNum128, pqc_cid=None) -> BigNum128:
        result_value = a.value - b.value
        if result_value < BigNum128.MIN_VALUE:
            raise OverflowError("CertifiedMath sub underflow")
        result = BigNum128(result_value)
        CertifiedMath._log_operation("sub", (a.value, b.value), result.value, pqc_cid)
        return result

    @staticmethod
    def _safe_mul(a: BigNum128, b: BigNum128, pqc_cid=None) -> BigNum128:
        result_value = (a.value * b.value) // BigNum128.SCALE
        if result_value > BigNum128.MAX_VALUE:
            raise OverflowError("CertifiedMath mul overflow")
        result = BigNum128(result_value)
        CertifiedMath._log_operation("mul", (a.value, b.value), result.value, pqc_cid)
        return result

    @staticmethod
    def _safe_div(a: BigNum128, b: BigNum128, pqc_cid=None) -> BigNum128:
        if b.value == 0:
            raise ZeroDivisionError("CertifiedMath div by zero")
        result_value = (a.value * BigNum128.SCALE) // b.value
        result = BigNum128(result_value)
        CertifiedMath._log_operation("div", (a.value, b.value), result.value, pqc_cid)
        return result

    # Step 3: Deterministic Fixed-Point Functions
    @staticmethod
    def fast_sqrt(a: BigNum128, iterations=20, pqc_cid=None) -> BigNum128:
        x = a.value
        if x == 0:
            return BigNum128(0)
        z = x
        for _ in range(iterations):
            z = (z + x * BigNum128.SCALE // z) // 2
            # Prevent division by zero in next iteration
            z = max(z, 1)
        result = BigNum128(z)
        CertifiedMath._log_operation("sqrt", (a.value,), result.value, pqc_cid)
        return result

    @staticmethod
    def calculate_phi_series(a: BigNum128, n: int, pqc_cid=None) -> BigNum128:
        phi = BigNum128(1618033988749894848)  # fixed-point phi*1e18
        result_value = a.value
        for i in range(n):
            result_value = (result_value * phi.value) // BigNum128.SCALE
            # Optional: log each multiplication step for granular audit
            # CertifiedMath._log_operation("phi_mul", (result_value, phi.value), result_value, pqc_cid)
        result = BigNum128(result_value)
        CertifiedMath._log_operation("phi_series", (a.value, n), result.value, pqc_cid)
        return result

    # Step 4: Deterministic Input Conversion
    @staticmethod
    def from_string(s: str) -> BigNum128:
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

    # Step 5: Public API
    @staticmethod
    def add(a: BigNum128, b: BigNum128, pqc_cid=None) -> BigNum128:
        return CertifiedMath._safe_add(a, b, pqc_cid)

    @staticmethod
    def sub(a: BigNum128, b: BigNum128, pqc_cid=None) -> BigNum128:
        return CertifiedMath._safe_sub(a, b, pqc_cid)

    @staticmethod
    def mul(a: BigNum128, b: BigNum128, pqc_cid=None) -> BigNum128:
        return CertifiedMath._safe_mul(a, b, pqc_cid)

    @staticmethod
    def div(a: BigNum128, b: BigNum128, pqc_cid=None) -> BigNum128:
        return CertifiedMath._safe_div(a, b, pqc_cid)