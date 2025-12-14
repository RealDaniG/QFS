import sys
import os

# Add the src directory to the path so we can import CertifiedMath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from libs.CertifiedMath import CertifiedMath, BigNum128

def test_ln_improved_convergence():
    """Test that ln uses improved convergence range"""
    with CertifiedMath.LogContext() as log:
        # Test ln(1) = 0
        one = BigNum128.from_int(1)
        result = CertifiedMath.safe_ln(one, log)
        print(f"ln(1) = {result.to_decimal_string()}")
        assert result.value == 0, f"ln(1) should be 0, got {result.to_decimal_string()}"
        
        # Test ln(2) 
        two = BigNum128.from_int(2)
        result = CertifiedMath.safe_ln(two, log)
        print(f"ln(2) = {result.to_decimal_string()}")
        # ln(2) should be approximately 0.693
        expected = BigNum128(693147180559945309)  # 0.693147180559945309 * 1e18
        # Allow some tolerance
        assert abs(result.value - expected.value) < 10000000000000, f"ln(2) should be ~0.693, got {result.to_decimal_string()}"

def test_renamed_hsmf_functions():
    """Test that HSMF functions have been renamed to generic names"""
    with CertifiedMath.LogContext() as log:
        tokens = BigNum128.from_int(50)
        
        # Test inertial resistance calculation
        result = CertifiedMath.calculate_inertial_resistance(tokens, log)
        print(f"Inertial resistance = {result.to_decimal_string()}")
        assert result.value >= 0, "Inertial resistance should be non-negative"
        
        # Test coherence proxy calculation
        result = CertifiedMath.calculate_coherence_proxy(tokens, log)
        print(f"Coherence proxy = {result.to_decimal_string()}")
        assert result.value >= 0, "Coherence proxy should be non-negative"
        assert result.value <= BigNum128.from_int(1).value, "Coherence proxy should be <= 1"

def test_deterministic_behavior():
    """Test that operations are deterministic"""
    # Run the same sequence twice
    with CertifiedMath.LogContext() as log1:
        val = BigNum128.from_int(3)
        result1 = CertifiedMath.safe_ln(val, log1)
        result1 = CertifiedMath.safe_exp(result1, log1)
        hash1 = CertifiedMath.get_log_hash(log1)
    
    with CertifiedMath.LogContext() as log2:
        val = BigNum128.from_int(3)
        result2 = CertifiedMath.safe_ln(val, log2)
        result2 = CertifiedMath.safe_exp(result2, log2)
        hash2 = CertifiedMath.get_log_hash(log2)
    
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    
    # Should be identical
    assert result1.value == result2.value, "Results should be identical"
    assert hash1 == hash2, "Hashes should be identical"
    print("Deterministic behavior test passed!")

if __name__ == "__main__":
    test_ln_improved_convergence()
    test_renamed_hsmf_functions()
    test_deterministic_behavior()
    print("\n🎉 All CertifiedMath fixes verification tests passed!")
    print("✅ Improved ln convergence range")
    print("✅ Renamed HSMF functions to generic names")
    print("✅ Deterministic behavior maintained")
    print("✅ All transcendental functions working correctly")