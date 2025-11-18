"""
Test cases for transcendentals functions in CertifiedMath
"""
import sys
import os

# Add the src directory to the path so we can import CertifiedMath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from libs.CertifiedMath import CertifiedMath, BigNum128

def test_exp_ln_inverse():
    """Test that exp and ln are inverse operations"""
    with CertifiedMath.LogContext() as log:
        # Test exp(ln(x)) = x for x = 2
        two = BigNum128.from_int(2)
        ln_two = CertifiedMath.safe_ln(two, log)
        exp_ln_two = CertifiedMath.safe_exp(ln_two, log)
        
        # Should be approximately equal to 2
        diff = abs(exp_ln_two.value - two.value)
        assert diff < 1000000000000, f"exp(ln(2)) should be ~2, got {exp_ln_two.to_decimal_string()}, diff: {diff}"

def test_pow_vs_exp_ln():
    """Test that pow(x,y) = exp(y*ln(x))"""
    with CertifiedMath.LogContext() as log:
        # Test pow(2, 3) = exp(3*ln(2))
        two = BigNum128.from_int(2)
        three = BigNum128.from_int(3)
        
        # Calculate 2^3 using pow
        pow_result = CertifiedMath.safe_pow(two, three, log)
        
        # Calculate 2^3 using exp(y*ln(x))
        ln_two = CertifiedMath.safe_ln(two, log)
        y_ln_x = CertifiedMath.safe_mul(three, ln_two, log)
        exp_result = CertifiedMath.safe_exp(y_ln_x, log)
        
        # Should be approximately equal
        diff = abs(pow_result.value - exp_result.value)
        assert diff < 1000000000000, f"pow(2,3) and exp(3*ln(2)) should be equal, pow: {pow_result.to_decimal_string()}, exp: {exp_result.to_decimal_string()}"

def test_sqrt_identity():
    """Test that sqrt(x^2) ≈ |x|"""
    with CertifiedMath.LogContext() as log:
        # Test sqrt(3^2) = 3
        three = BigNum128.from_int(3)
        three_squared = CertifiedMath.safe_mul(three, three, log)
        sqrt_result = CertifiedMath.fast_sqrt(three_squared, log)
        
        # Should be approximately equal to 3
        diff = abs(sqrt_result.value - three.value)
        assert diff < 1000000000000, f"sqrt(3^2) should be ~3, got {sqrt_result.to_decimal_string()}, diff: {diff}"

def test_deterministic_sequence():
    """Test deterministic replay of a sequence of operations"""
    # Run the same sequence twice and ensure results and logs are identical
    with CertifiedMath.LogContext() as log1:
        val = BigNum128.from_int(2)
        result1 = CertifiedMath.safe_ln(val, log1)
        result1 = CertifiedMath.safe_exp(result1, log1)
        result1 = CertifiedMath.safe_phi_series(result1, log1)
        result1 = CertifiedMath.safe_mul(result1, val, log1)
        hash1 = CertifiedMath.get_log_hash(log1)
    
    with CertifiedMath.LogContext() as log2:
        val = BigNum128.from_int(2)
        result2 = CertifiedMath.safe_ln(val, log2)
        result2 = CertifiedMath.safe_exp(result2, log2)
        result2 = CertifiedMath.safe_phi_series(result2, log2)
        result2 = CertifiedMath.safe_mul(result2, val, log2)
        hash2 = CertifiedMath.get_log_hash(log2)
    
    assert result1.value == result2.value, "Sequence should produce deterministic results"
    assert hash1 == hash2, "Log hashes should be identical for deterministic operations"

if __name__ == "__main__":
    test_exp_ln_inverse()
    test_pow_vs_exp_ln()
    test_sqrt_identity()
    test_deterministic_sequence()
    print("All transcendental tests passed!")