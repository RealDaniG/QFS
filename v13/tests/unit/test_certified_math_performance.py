"""
Performance testing for CertifiedMath to validate TPS targets and optimization strategies.
"""
<<<<<<< HEAD

import sys
import os
from time import perf_counter

# Add the libs directory to the path

from CertifiedMath import CertifiedMath, BigNum128, LogContext


def test_basic_operations_performance():
    """Test performance of basic arithmetic operations."""
    print("Testing basic arithmetic operations performance...")

    # Create a log list for deterministic operations
    audit_log_store = []

    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)

        # Create test values
        a = BigNum128.from_string("123.456789")
        b = BigNum128.from_string("987.654321")

        # Test addition performance
        start_time = perf_counter()
        operations = 10000
        for i in range(operations):
            result = cm.add(a, b, pqc_cid=f"PERF_ADD_{i}")
        end_time = perf_counter()

        duration = end_time - start_time
        tps = operations / duration
        print(f"  Addition: {operations} operations in {duration:.4f}s = {tps:.2f} TPS")

        # Test multiplication performance
        start_time = perf_counter()
        for i in range(operations):
            result = cm.mul(a, b, pqc_cid=f"PERF_MUL_{i}")
        end_time = perf_counter()

        duration = end_time - start_time
        tps = operations / duration
        print(
            f"  Multiplication: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )

        # Test division performance
        start_time = perf_counter()
        for i in range(operations):
            result = cm.div(a, b, pqc_cid=f"PERF_DIV_{i}")
        end_time = perf_counter()

=======
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
from CertifiedMath import CertifiedMath, BigNum128, LogContext

def test_basic_operations_performance():
    """Test performance of basic arithmetic operations."""
    print('Testing basic arithmetic operations performance...')
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        a = BigNum128.from_string('123.456789')
        b = BigNum128.from_string('987.654321')
        start_time = det_time_now()
        operations = 10000
        for i in range(operations):
            result = cm.add(a, b, pqc_cid=f'PERF_ADD_{i}')
        end_time = det_time_now()
        duration = end_time - start_time
        tps = operations / duration
        print(f'  Addition: {operations} operations in {duration:.4f}s = {tps:.2f} TPS')
        start_time = det_time_now()
        for i in range(operations):
            result = cm.mul(a, b, pqc_cid=f'PERF_MUL_{i}')
        end_time = det_time_now()
        duration = end_time - start_time
        tps = operations / duration
        print(f'  Multiplication: {operations} operations in {duration:.4f}s = {tps:.2f} TPS')
        start_time = det_time_now()
        for i in range(operations):
            result = cm.div(a, b, pqc_cid=f'PERF_DIV_{i}')
        end_time = det_time_now()
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        duration = end_time - start_time
        tps = operations / duration
        print(f'  Division: {operations} operations in {duration:.4f}s = {tps:.2f} TPS')

def test_transcendental_operations_performance():
    """Test performance of transcendental operations."""
<<<<<<< HEAD
    print("Testing transcendental operations performance...")

    # Create a log list for deterministic operations
    audit_log_store = []

    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)

        # Create test values
        a = BigNum128.from_string("0.5")
        b = BigNum128.from_string("1.5")

        # Test sqrt performance
        start_time = perf_counter()
        operations = 1000
        for i in range(operations):
            result = cm.sqrt(a, pqc_cid=f"PERF_SQRT_{i}")
        end_time = perf_counter()

        duration = end_time - start_time
        tps = operations / duration
        print(
            f"  Square Root: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )

        # Test exp performance
        start_time = perf_counter()
        for i in range(operations):
            result = cm.exp(a, pqc_cid=f"PERF_EXP_{i}")
        end_time = perf_counter()

        duration = end_time - start_time
        tps = operations / duration
        print(
            f"  Exponential: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )

        # Test ln performance
        start_time = perf_counter()
        for i in range(operations):
            result = cm.ln(b, pqc_cid=f"PERF_LN_{i}")
        end_time = perf_counter()

        duration = end_time - start_time
        tps = operations / duration
        print(
            f"  Natural Log: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )


def test_phi_series_performance():
    """Test performance of phi series operations."""
    print("Testing phi series performance...")

    # Create a log list for deterministic operations
    audit_log_store = []

    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)

        # Create test values
        a = BigNum128.from_string("0.1")

        # Test phi_series performance
        start_time = perf_counter()
        operations = 1000
        for i in range(operations):
            result = cm.phi_series(a, pqc_cid=f"PERF_PHI_{i}")
        end_time = perf_counter()

        duration = end_time - start_time
        tps = operations / duration
        print(
            f"  Phi Series: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )


def test_two_power_performance():
    """Test performance of two to the power operations."""
    print("Testing two to the power performance...")

    # Create a log list for deterministic operations
    audit_log_store = []

    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)

        # Create test values
        a = BigNum128.from_string("1.0")

        # Test two_to_the_power performance
        start_time = perf_counter()
        operations = 1000
        for i in range(operations):
            result = cm.two_to_the_power(a, pqc_cid=f"PERF_TWO_POW_{i}")
        end_time = perf_counter()

        duration = end_time - start_time
        tps = operations / duration
        print(
            f"  Two to the Power: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )


def test_composite_operations_performance():
    """Test performance of composite operations."""
    print("Testing composite operations performance...")

    # Create a log list for deterministic operations
    audit_log_store = []

    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)

        # Create test values
        atr_state = BigNum128.from_string("100.0")
        res_state = BigNum128.from_string("99.8")

        # Test update_tokens performance
        start_time = perf_counter()
        operations = 100
        for i in range(operations):
            atr_new, res_new, psi_sync = cm.update_tokens(
                atr_state,
                res_state,
                pqc_cid=f"PERF_UPDATE_{i}",
                quantum_metadata={"test": "performance"},
            )
        end_time = perf_counter()

        duration = end_time - start_time
        tps = operations / duration
        print(
            f"  Update Tokens: {operations} operations in {duration:.4f}s = {tps:.2f} TPS"
        )
        print(f"  Note: Each update_tokens operation includes multiple sub-operations")


def run_performance_tests():
    """Run all performance tests."""
    print("Running CertifiedMath Performance Tests...")
    print("=" * 60)

=======
    print('Testing transcendental operations performance...')
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        a = BigNum128.from_string('0.5')
        b = BigNum128.from_string('1.5')
        start_time = det_time_now()
        operations = 1000
        for i in range(operations):
            result = cm.sqrt(a, pqc_cid=f'PERF_SQRT_{i}')
        end_time = det_time_now()
        duration = end_time - start_time
        tps = operations / duration
        print(f'  Square Root: {operations} operations in {duration:.4f}s = {tps:.2f} TPS')
        start_time = det_time_now()
        for i in range(operations):
            result = cm.exp(a, pqc_cid=f'PERF_EXP_{i}')
        end_time = det_time_now()
        duration = end_time - start_time
        tps = operations / duration
        print(f'  Exponential: {operations} operations in {duration:.4f}s = {tps:.2f} TPS')
        start_time = det_time_now()
        for i in range(operations):
            result = cm.ln(b, pqc_cid=f'PERF_LN_{i}')
        end_time = det_time_now()
        duration = end_time - start_time
        tps = operations / duration
        print(f'  Natural Log: {operations} operations in {duration:.4f}s = {tps:.2f} TPS')

def test_phi_series_performance():
    """Test performance of phi series operations."""
    print('Testing phi series performance...')
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        a = BigNum128.from_string('0.1')
        start_time = det_time_now()
        operations = 1000
        for i in range(operations):
            result = cm.phi_series(a, pqc_cid=f'PERF_PHI_{i}')
        end_time = det_time_now()
        duration = end_time - start_time
        tps = operations / duration
        print(f'  Phi Series: {operations} operations in {duration:.4f}s = {tps:.2f} TPS')

def test_two_power_performance():
    """Test performance of two to the power operations."""
    print('Testing two to the power performance...')
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        a = BigNum128.from_string('1.0')
        start_time = det_time_now()
        operations = 1000
        for i in range(operations):
            result = cm.two_to_the_power(a, pqc_cid=f'PERF_TWO_POW_{i}')
        end_time = det_time_now()
        duration = end_time - start_time
        tps = operations / duration
        print(f'  Two to the Power: {operations} operations in {duration:.4f}s = {tps:.2f} TPS')

def test_composite_operations_performance():
    """Test performance of composite operations."""
    print('Testing composite operations performance...')
    audit_log_store = []
    with LogContext(audit_log_store) as ctx_log:
        cm = CertifiedMath(ctx_log)
        atr_state = BigNum128.from_string('100.0')
        res_state = BigNum128.from_string('99.8')
        start_time = det_time_now()
        operations = 100
        for i in range(operations):
            atr_new, res_new, psi_sync = cm.update_tokens(atr_state, res_state, pqc_cid=f'PERF_UPDATE_{i}', quantum_metadata={'test': 'performance'})
        end_time = det_time_now()
        duration = end_time - start_time
        tps = operations / duration
        print(f'  Update Tokens: {operations} operations in {duration:.4f}s = {tps:.2f} TPS')
        print(f'  Note: Each update_tokens operation includes multiple sub-operations')

def run_performance_tests():
    """Run all performance tests."""
    print('Running CertifiedMath Performance Tests...')
    print('=' * 60)
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
    test_basic_operations_performance()
    test_transcendental_operations_performance()
    test_phi_series_performance()
    test_two_power_performance()
    test_composite_operations_performance()
<<<<<<< HEAD

    print("=" * 60)
    print("[SUCCESS] All CertifiedMath Performance tests completed!")


if __name__ == "__main__":
    run_performance_tests()
=======
    print('=' * 60)
    print('[SUCCESS] All CertifiedMath Performance tests completed!')
if __name__ == '__main__':
    run_performance_tests()
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
