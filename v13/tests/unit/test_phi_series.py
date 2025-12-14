"""
Test cases for the _safe_phi_series function in CertifiedMath
"""
import sys
import os


from v13.libs.CertifiedMath import CertifiedMath, BigNum128

def test_phi_series_basic_values():
    """Test phi_series function with basic values"""
    with CertifiedMath.LogContext() as log:
        # Test φ(0) = 0
        zero = BigNum128(0)
        result = CertifiedMath.safe_phi_series(zero, log)
        expected = BigNum128(0)
        assert result.value == expected.value, f"φ(0) should be 0, got {result.to_decimal_string()}"
        
        # Test φ(1) 
        one = BigNum128.from_int(1)
        result = CertifiedMath.safe_phi_series(one, log, n=10)
        # φ(1) = 1 - 1/3 + 1/5 - 1/7 + ... ≈ 0.785
        # Using 10 terms should give us a reasonable approximation
        assert result.value > 0, f"φ(1) should be positive, got {result.to_decimal_string()}"

def test_phi_series_negative_values():
    """Test phi_series function with negative values"""
    with CertifiedMath.LogContext() as log:
        # Test φ(-1)
        neg_one = BigNum128.from_int(-1)
        result = CertifiedMath.safe_phi_series(neg_one, log, n=10)
        # φ(-1) = -1 + 1/3 - 1/5 + 1/7 - ... ≈ -0.785
        assert result.value < 0, f"φ(-1) should be negative, got {result.to_decimal_string()}"

def test_phi_series_half_values():
    """Test phi_series function with 0.5"""
    with CertifiedMath.LogContext() as log:
        # Test φ(0.5)
        half = BigNum128(500000000000000000)  # 0.5 * 1e18
        result = CertifiedMath.safe_phi_series(half, log, n=20)
        # φ(0.5) should converge to a value between 0 and 1
        assert result.value > 0, f"φ(0.5) should be positive, got {result.to_decimal_string()}"
        assert result.value < BigNum128.from_int(1).value, f"φ(0.5) should be less than 1, got {result.to_decimal_string()}"

def test_phi_series_deterministic():
    """Test that phi_series produces deterministic results"""
    # Run the same calculation twice and ensure results are identical
    with CertifiedMath.LogContext() as log1:
        val = BigNum128.from_int(1)
        result1 = CertifiedMath.safe_phi_series(val, log1, n=15)
        hash1 = CertifiedMath.get_log_hash(log1)
    
    with CertifiedMath.LogContext() as log2:
        val = BigNum128.from_int(1)
        result2 = CertifiedMath.safe_phi_series(val, log2, n=15)
        hash2 = CertifiedMath.get_log_hash(log2)
    
    assert result1.value == result2.value, "phi_series should produce deterministic results"
    assert hash1 == hash2, "Log hashes should be identical for deterministic operations"

def test_phi_series_convergence():
    """Test that increasing terms improves convergence"""
    with CertifiedMath.LogContext() as log10:
        val = BigNum128.from_int(1)
        result10 = CertifiedMath.safe_phi_series(val, log10, n=10)
    
    with CertifiedMath.LogContext() as log20:
        val = BigNum128.from_int(1)
        result20 = CertifiedMath.safe_phi_series(val, log20, n=20)
    
    # With more terms, results should be closer to the true value (which we approximate as the 20-term result)
    # We're not checking exact values, just that they're close
    diff = abs(result10.value - result20.value)
    assert diff < 10000000000000, f"Results should converge with more terms, diff: {diff}"

if __name__ == "__main__":
    test_phi_series_basic_values()
    test_phi_series_negative_values()
    test_phi_series_half_values()
    test_phi_series_deterministic()
    test_phi_series_convergence()
    print("All phi_series tests passed!")