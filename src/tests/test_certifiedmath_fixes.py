"""
Test file to verify the fixes to CertifiedMath.py
"""
import sys
import pathlib

# Add the src directory to the path so we can import the modules
src_path = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(src_path / 'libs'))

# Import the modules directly without relative imports
from libs.BigNum128 import BigNum128
from libs.CertifiedMath import CertifiedMath

def test_safe_ln():
    """Test the _safe_ln function"""
    print("Testing _safe_ln function...")
    log_list = []
    
    # Test with a simple value
    a = BigNum128.from_int(1)  # ln(1) = 0
    result = CertifiedMath.ln(a, 10, log_list)
    print(f"ln(1) = {result.to_decimal_string()}")
    assert result.value == 0, f"Expected 0, got {result.value}"
    
    # Test with e (should be approximately 1)
    # e ≈ 2.718281828459045235
    e = BigNum128(2718281828459045235)
    result = CertifiedMath.ln(e, 20, log_list)
    print(f"ln(e) = {result.to_decimal_string()}")
    # Should be close to 1
    assert abs(result.value - BigNum128.SCALE) < BigNum128.SCALE // 100, f"ln(e) should be close to 1, got {result.to_decimal_string()}"
    
    print("✓ _safe_ln tests passed")

def test_safe_phi_series():
    """Test the _safe_phi_series function (arctangent series)"""
    print("Testing _safe_phi_series function...")
    log_list = []
    
    # Test with 0 (should be 0)
    x = BigNum128(0)
    result = CertifiedMath.phi_series(x, 10, log_list)
    print(f"phi_series(0) = {result.to_decimal_string()}")
    assert result.value == 0, f"Expected 0, got {result.value}"
    
    # Test with a small value
    x = BigNum128.from_int(1)  # x = 1
    result = CertifiedMath.phi_series(x, 50, log_list)
    print(f"phi_series(1) = {result.to_decimal_string()}")
    # arctan(1) = π/4 ≈ 0.7853981633974483096
    expected = BigNum128(785398163397448309)
    print(f"Expected π/4 = {expected.to_decimal_string()}")
    # Should be close to π/4, but allow for more tolerance due to series convergence
    assert abs(result.value - expected.value) < BigNum128.SCALE // 10, f"phi_series(1) should be close to π/4, got {result.to_decimal_string()}"
    
    print("✓ _safe_phi_series tests passed")

def test_safe_operations():
    """Test basic safe operations"""
    print("Testing basic safe operations...")
    log_list = []
    
    # Test addition
    a = BigNum128.from_int(1)
    b = BigNum128.from_int(2)
    result = CertifiedMath.add(a, b, log_list)
    print(f"1 + 2 = {result.to_decimal_string()}")
    assert result.value == 3 * BigNum128.SCALE, f"Expected 3, got {result.to_decimal_string()}"
    
    # Test multiplication
    result = CertifiedMath.mul(a, b, log_list)
    print(f"1 * 2 = {result.to_decimal_string()}")
    assert result.value == 2 * BigNum128.SCALE, f"Expected 2, got {result.to_decimal_string()}"
    
    print("✓ Basic safe operations tests passed")

def main():
    """Run all tests"""
    print("Running CertifiedMath fixes verification tests...")
    print("=" * 50)
    
    try:
        test_safe_operations()
        test_safe_ln()
        test_safe_phi_series()
        
        print("=" * 50)
        print("✓ All tests passed! CertifiedMath fixes are working correctly.")
        return True
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)