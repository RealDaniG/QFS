"""
Performance testing for CertifiedMath to validate TPS targets and optimization strategies.
"""

from v13.libs.deterministic_helpers import (
    ZeroSimAbort,
    det_time_now,
    det_perf_counter,
    det_random,
    qnum,
)
from CertifiedMath import CertifiedMath, BigNum128, LogContext
from v13.tests.conftest import QFSLogger, LogCategory


def test_basic_operations_performance():
    """Test performance of basic arithmetic operations."""
    print("Testing basic arithmetic operations performance...")
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        a = BigNum128.from_string("123.456789")
        b = BigNum128.from_string("987.654321")
        start_time = det_time_now()
        operations = 10000
        for i in range(operations):
            result = cm.add(a, b, pqc_cid=f"PERF_ADD_{i}")
        end_time = det_time_now()
        duration = end_time - start_time
        if duration > 0:
            tps = operations / duration
        else:
            tps = float("inf")
        print(f"  Addition: {operations} operations in {duration:.4f}s = {tps:.2f} TPS")

        start_time = det_time_now()
        for i in range(operations):
            result = cm.mul(a, b, pqc_cid=f"PERF_MUL_{i}")
        end_time = det_time_now()
        duration = end_time - start_time
        if duration > 0:
            tps = operations / duration
        else:
            tps = float("inf")
        print(
            f"  Multiplication: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )

        start_time = det_time_now()
        for i in range(operations):
            result = cm.div(a, b, pqc_cid=f"PERF_DIV_{i}")
        end_time = det_time_now()
        duration = end_time - start_time
        if duration > 0:
            tps = operations / duration
        else:
            tps = float("inf")
        print(f"  Division: {operations} operations in {duration:.4f}s = {tps:.2f} TPS")


def test_transcendental_operations_performance():
    """Test performance of transcendental operations."""
    print("Testing transcendental operations performance...")
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        a = BigNum128.from_string("0.5")
        b = BigNum128.from_string("1.5")

        start_time = det_time_now()
        operations = 1000
        for i in range(operations):
            result = cm.sqrt(a, pqc_cid=f"PERF_SQRT_{i}")
        end_time = det_time_now()
        duration = end_time - start_time
        if duration > 0:
            tps = operations / duration
        else:
            tps = float("inf")
        print(
            f"  Square Root: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )

        start_time = det_time_now()
        for i in range(operations):
            result = cm.exp(a, pqc_cid=f"PERF_EXP_{i}")
        end_time = det_time_now()
        duration = end_time - start_time
        if duration > 0:
            tps = operations / duration
        else:
            tps = float("inf")
        print(
            f"  Exponential: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )

        start_time = det_time_now()
        for i in range(operations):
            result = cm.ln(b, pqc_cid=f"PERF_LN_{i}")
        end_time = det_time_now()
        duration = end_time - start_time
        if duration > 0:
            tps = operations / duration
        else:
            tps = float("inf")
        print(
            f"  Natural Log: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )


def test_phi_series_performance():
    """Test performance of phi series operations."""
    print("Testing phi series performance...")
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        a = BigNum128.from_string("0.1")
        start_time = det_time_now()
        operations = 1000
        for i in range(operations):
            result = cm.phi_series(a, pqc_cid=f"PERF_PHI_{i}")
        end_time = det_time_now()
        duration = end_time - start_time
        if duration > 0:
            tps = operations / duration
        else:
            tps = float("inf")
        print(
            f"  Phi Series: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )


def test_two_power_performance():
    """Test performance of two to the power operations."""
    print("Testing two to the power performance...")
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        a = BigNum128.from_string("1.0")
        start_time = det_time_now()
        operations = 1000
        for i in range(operations):
            result = cm.two_to_the_power(a, pqc_cid=f"PERF_TWO_POW_{i}")
        end_time = det_time_now()
        duration = end_time - start_time
        if duration > 0:
            tps = operations / duration
        else:
            tps = float("inf")
        print(
            f"  Two to the Power: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )


def test_composite_operations_performance():
    """Test performance of composite operations."""
    print("Testing composite operations performance...")
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        atr_state = BigNum128.from_string("100.0")
        res_state = BigNum128.from_string("99.8")
        start_time = det_time_now()
        operations = 100
        for i in range(operations):
            atr_new, res_new, psi_sync = cm.update_tokens(
                atr_state,
                res_state,
                pqc_cid=f"PERF_UPDATE_{i}",
                quantum_metadata={"test": "performance"},
            )
        end_time = det_time_now()
        duration = end_time - start_time
        if duration > 0:
            tps = operations / duration
        else:
            tps = float("inf")
        print(
            f"  Update Tokens: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )
        print(f"  Note: Each update_tokens operation includes multiple sub-operations")


def run_performance_tests():
    """Run all performance tests."""
    print("Running CertifiedMath Performance Tests...")
    print("=" * 60)
    test_basic_operations_performance()
    test_transcendental_operations_performance()
    test_phi_series_performance()
    test_two_power_performance()
    test_composite_operations_performance()
    print("=" * 60)
    print("[SUCCESS] All CertifiedMath Performance tests completed!")


if __name__ == "__main__":
    run_performance_tests()
