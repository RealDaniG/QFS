"""
Comprehensive Test Suite for CertifiedMath.py
Tests all functionality including the missing audit steps identified for QFS V13 compliance.
"""

import sys
import os
import json
import tempfile

# Add the libs directory to the path so we can import CertifiedMath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libs.CertifiedMath import CertifiedMath, BigNum128


def test_fixed_point_arithmetic():
    """Test fixed-point arithmetic operations"""
    print("Testing fixed-point arithmetic operations...")
    
    # Test normal operations
    a = BigNum128(1000000000000000000)  # 1.0
    b = BigNum128(2000000000000000000)  # 2.0
    
    # Test addition
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.add(a, b, log_list)
        assert result.value == 3000000000000000000
        assert len(log_list) == 1
        assert log_list[0]["op_name"] == "add"
        print("✓ Addition test passed")
    
    # Test subtraction
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.sub(b, a, log_list)
        assert result.value == 1000000000000000000
        assert len(log_list) == 1
        assert log_list[0]["op_name"] == "sub"
        print("✓ Subtraction test passed")
    
    # Test multiplication
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.mul(a, b, log_list)
        # 1.0 * 2.0 = 2.0 (scaled)
        assert result.value == 2000000000000000000
        assert len(log_list) == 1
        assert log_list[0]["op_name"] == "mul"
        print("✓ Multiplication test passed")
    
    # Test division
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.div(b, a, log_list)
        # 2.0 / 1.0 = 2.0 (scaled)
        assert result.value == 2000000000000000000
        assert len(log_list) == 1
        assert log_list[0]["op_name"] == "div"
        print("✓ Division test passed")


def test_boundary_conditions():
    """Test boundary conditions and edge cases"""
    print("\nTesting boundary conditions...")
    
    # Test with zero
    zero = BigNum128(0)
    one = BigNum128(1000000000000000000)  # 1.0
    
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.add(zero, one, log_list)
        assert result.value == 1000000000000000000
        print("✓ Zero addition test passed")
    
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.mul(zero, one, log_list)
        assert result.value == 0
        print("✓ Zero multiplication test passed")
    
    # Test with maximum values
    max_val = BigNum128(BigNum128.MAX_VALUE)
    min_val = BigNum128(BigNum128.MIN_VALUE)
    
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.add(min_val, min_val, log_list)
        assert result.value == 0
        print("✓ Minimum value addition test passed")


def test_overflow_underflow():
    """Test overflow and underflow conditions"""
    print("\nTesting overflow and underflow...")
    
    # Test addition overflow
    max_val = BigNum128(BigNum128.MAX_VALUE)
    one = BigNum128(1)
    
    try:
        with CertifiedMath.LogContext() as log_list:
            CertifiedMath.add(max_val, one, log_list)
        assert False, "Should have raised OverflowError"
    except OverflowError:
        print("✓ Addition overflow test passed")
    
    # Test subtraction underflow
    min_val = BigNum128(BigNum128.MIN_VALUE)
    one = BigNum128(1)
    
    try:
        with CertifiedMath.LogContext() as log_list:
            CertifiedMath.sub(min_val, one, log_list)
        assert False, "Should have raised OverflowError"
    except OverflowError:
        print("✓ Subtraction underflow test passed")
    
    # Test division by zero
    a = BigNum128(1000000000000000000)
    zero = BigNum128(0)
    
    try:
        with CertifiedMath.LogContext() as log_list:
            CertifiedMath.div(a, zero, log_list)
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError:
        print("✓ Division by zero test passed")


def test_deterministic_functions():
    """Test deterministic functions like sqrt and phi_series"""
    print("\nTesting deterministic functions...")
    
    # Test fast_sqrt with zero
    zero = BigNum128(0)
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.fast_sqrt(zero, log_list)
        assert result.value == 0
        assert len(log_list) == 1
        assert log_list[0]["op_name"] == "sqrt"
        print("✓ Square root of zero test passed")
    
    # Test fast_sqrt with perfect square
    four = BigNum128(4000000000000000000)  # 4.0
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.fast_sqrt(four, log_list, iterations=20)
        # Should be approximately 2.0
        assert abs(result.value - 2000000000000000000) < 100000000000000  # Within tolerance
        print("✓ Square root of perfect square test passed")
    
    # Test calculate_phi_series with n=0
    a = BigNum128(1000000000000000000)  # 1.0
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.calculate_phi_series(a, log_list, n=0)
        # Should be the same as input when n=0
        assert result.value == 1000000000000000000
        print("✓ Phi series with n=0 test passed")


def test_iteration_limits():
    """Test iteration limits for defensive programming"""
    print("\nTesting iteration limits...")
    
    a = BigNum128(1000000000000000000)  # 1.0
    
    # Test exceeding MAX_SQRT_ITERATIONS
    try:
        with CertifiedMath.LogContext() as log_list:
            CertifiedMath.fast_sqrt(a, log_list, iterations=CertifiedMath.MAX_SQRT_ITERATIONS + 1)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ Square root iteration limit test passed")
    
    # Test exceeding MAX_PHI_SERIES_TERMS
    try:
        with CertifiedMath.LogContext() as log_list:
            CertifiedMath.calculate_phi_series(a, log_list, n=CertifiedMath.MAX_PHI_SERIES_TERMS + 1)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ Phi series iteration limit test passed")


def test_input_conversion():
    """Test input conversion from string"""
    print("\nTesting input conversion...")
    
    # Test normal input (integer string)
    result = CertifiedMath.from_string("1")
    assert result.value == 1000000000000000000  # 1 * 10^18
    print("✓ Normal string input test passed")
    
    # Test decimal input
    result = CertifiedMath.from_string("1.0")
    assert result.value == 1000000000000000000  # 1.0 * 10^18
    print("✓ Decimal string input test passed")
    
    # Test invalid input (non-digit)
    try:
        CertifiedMath.from_string("abc")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ Invalid string input test passed")
    
    # Test invalid input (non-string)
    try:
        CertifiedMath.from_string(123)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        print("✓ Non-string input test passed")


def test_public_wrapper_log_list_enforcement():
    """Test that all public wrappers require log_list parameter (Missing Audit Step 2)"""
    print("\nTesting public wrapper log_list enforcement (Missing Audit Step 2)...")
    
    a = BigNum128(1000000000000000000)  # 1.0
    b = BigNum128(2000000000000000000)  # 2.0
    
    # Test add without log_list
    try:
        # We're intentionally passing None to test the enforcement
        # Type checking is disabled for this specific test case
        CertifiedMath.add(a, b, None)  # type: ignore
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "log_list is required" in str(e)
        print("✓ Add log_list enforcement test passed")
    
    # Test sub without log_list
    try:
        # We're intentionally passing None to test the enforcement
        # Type checking is disabled for this specific test case
        CertifiedMath.sub(a, b, None)  # type: ignore
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "log_list is required" in str(e)
        print("✓ Sub log_list enforcement test passed")
    
    # Test mul without log_list
    try:
        # We're intentionally passing None to test the enforcement
        # Type checking is disabled for this specific test case
        CertifiedMath.mul(a, b, None)  # type: ignore
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "log_list is required" in str(e)
        print("✓ Mul log_list enforcement test passed")
    
    # Test div without log_list
    try:
        # We're intentionally passing None to test the enforcement
        # Type checking is disabled for this specific test case
        CertifiedMath.div(a, b, None)  # type: ignore
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "log_list is required" in str(e)
        print("✓ Div log_list enforcement test passed")
    
    # Test fast_sqrt without log_list
    try:
        # We're intentionally passing None to test the enforcement
        # Type checking is disabled for this specific test case
        CertifiedMath.fast_sqrt(a, None)  # type: ignore
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "log_list is required" in str(e)
        print("✓ Fast sqrt log_list enforcement test passed")
    
    # Test calculate_phi_series without log_list
    try:
        # We're intentionally passing None to test the enforcement
        # Type checking is disabled for this specific test case
        CertifiedMath.calculate_phi_series(a, None)  # type: ignore
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "log_list is required" in str(e)
        print("✓ Phi series log_list enforcement test passed")


def test_deterministic_replay():
    """Test deterministic replay of a sequence of operations."""
    print("\nTesting deterministic replay...")
    
    a = BigNum128(1000000000000000000)  # 1.0
    b = BigNum128(2000000000000000000)  # 2.0
    c = BigNum128(500000000000000000)   # 0.5
    
    # Perform a sequence of operations and capture the log
    with CertifiedMath.LogContext() as log_list:
        r1 = CertifiedMath.add(a, b, log_list)
        r2 = CertifiedMath.mul(r1, c, log_list)
        r3 = CertifiedMath.div(r2, a, log_list)
        initial_hash = CertifiedMath.get_log_hash(log_list)
        initial_result = r3.value
    
    # Perform the same sequence again
    with CertifiedMath.LogContext() as log_list_replay:
        r1_replay = CertifiedMath.add(a, b, log_list_replay)
        r2_replay = CertifiedMath.mul(r1_replay, c, log_list_replay)
        r3_replay = CertifiedMath.div(r2_replay, a, log_list_replay)
        replay_hash = CertifiedMath.get_log_hash(log_list_replay)
        replay_result = r3_replay.value
    
    # Results and hashes should be identical
    assert initial_result == replay_result, f"Replay result mismatch: {initial_result} vs {replay_result}"
    assert initial_hash == replay_hash, f"Replay hash mismatch: {initial_hash} vs {replay_hash}"
    print("✓ Deterministic replay test passed")

def test_determinism():
    """Test that operations are deterministic"""
    print("\nTesting determinism...")
    
    a = BigNum128(1000000000000000000)  # 1.0
    b = BigNum128(2000000000000000000)  # 2.0
    
    # Run the same sequence multiple times
    hashes = []
    for i in range(3):
        with CertifiedMath.LogContext() as log_list:
            r1 = CertifiedMath.add(a, b, log_list, pqc_cid="pqc_001")
            r2 = CertifiedMath.mul(r1, a, log_list, pqc_cid="pqc_002")
            hash_val = CertifiedMath.get_log_hash(log_list)
            hashes.append(hash_val)
    
    # All hashes should be identical
    assert all(h == hashes[0] for h in hashes), "Deterministic hashes do not match"
    print("✓ Determinism test passed")


def test_default_iterations_terms():
    """Test that public wrappers use correct default iterations/terms."""
    print("\nTesting default iterations/terms...")
    
    a = BigNum128(1000000000000000000)  # 1.0
    
    # Test fast_sqrt default
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.fast_sqrt(a, log_list)  # No iterations specified
        # Check if the log entry correctly records the default (20)
        assert log_list[0]["inputs"][1] == 20  # Check if the internal function received 20
        print("✓ Fast sqrt default iterations test passed")
    
    # Test calculate_phi_series default
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.calculate_phi_series(a, log_list)  # No n specified
        # Check if the log entry correctly records the default (50)
        assert log_list[0]["inputs"][1] == 50  # Check if the internal function received 50
        print("✓ Phi series default terms test passed")

def test_log_context_helpers():
    """Test LogContext helper methods."""
    print("\nTesting LogContext helpers...")
    
    a = BigNum128(1000000000000000000)  # 1.0
    b = BigNum128(2000000000000000000)  # 2.0
    
    # Test the LogContext methods directly
    ctx = CertifiedMath.LogContext()
    log_list = ctx.__enter__()
    
    try:
        CertifiedMath.add(a, b, log_list)
        CertifiedMath.sub(b, a, log_list)
        
        # Test get_log
        log = ctx.get_log()
        assert len(log) == 2
        
        # Test get_hash
        hash_val = ctx.get_hash()
        expected_hash = CertifiedMath.get_log_hash(log_list)
        assert hash_val == expected_hash
        
        # Test export (similar to existing export test, but via context)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as f:
            temp_path = f.name
        try:
            ctx.export(temp_path)
            with open(temp_path, 'r') as f:
                exported_data = json.load(f)
            assert len(exported_data) == 2
            print("✓ LogContext helpers test passed")
        finally:
            os.unlink(temp_path)
    finally:
        ctx.__exit__(None, None, None)

def test_logging_and_hashing():
    """Test logging structure and hashing"""
    print("\nTesting logging and hashing...")
    
    a = BigNum128(1000000000000000000)  # 1.0
    b = BigNum128(2000000000000000000)  # 2.0
    
    with CertifiedMath.LogContext() as log_list:
        result = CertifiedMath.add(a, b, log_list, 
                                  pqc_cid="test-pqc-cid-001",
                                  quantum_metadata={"quantum_seed": "qrng-001"})
        
        # Check log structure
        assert len(log_list) == 1
        log_entry = log_list[0]
        required_keys = {"op_name", "inputs", "result", "pqc_cid", "quantum_metadata"}
        assert all(key in log_entry for key in required_keys), f"Missing keys in log entry: {required_keys - log_entry.keys()}"
        
        # Check values
        assert log_entry["op_name"] == "add"
        assert log_entry["inputs"] == (a.value, b.value)
        assert log_entry["result"] == result.value
        assert log_entry["pqc_cid"] == "test-pqc-cid-001"
        
        # Check hash consistency
        hash1 = CertifiedMath.get_log_hash(log_list)
        hash2 = CertifiedMath.get_log_hash(log_list)
        assert hash1 == hash2, "Hashes should be consistent"
        
        # Test export functionality
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            CertifiedMath.export_log(log_list, temp_path)
            with open(temp_path, 'r') as f:
                exported_data = json.load(f)
            assert len(exported_data) == 1
            assert exported_data[0]["op_name"] == "add"
            print("✓ Logging and hashing test passed")
        finally:
            os.unlink(temp_path)


def run_all_tests():
    """Run all tests"""
    print("Running CertifiedMath Test Suite")
    print("=" * 50)
    
    test_fixed_point_arithmetic()
    test_boundary_conditions()
    test_overflow_underflow()
    test_deterministic_functions()
    test_iteration_limits()
    test_input_conversion()
    test_public_wrapper_log_list_enforcement()
    # test_quantum_metadata_filtering()  # Removed per V13 plan (upstream validation)
    test_deterministic_replay()
    test_default_iterations_terms()
    test_log_context_helpers()
    test_determinism()
    test_logging_and_hashing()
    
    print("\n" + "=" * 50)
    print("All tests passed! CertifiedMath is ready for QFS V13.")


if __name__ == "__main__":
    run_all_tests()