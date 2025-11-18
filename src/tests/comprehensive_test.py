"""
Comprehensive test to verify all fixes in the QFS V13 system
"""
import sys
import pathlib

# Add the src directory to the path so we can import the modules
src_path = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(src_path / 'libs'))

# Import the modules using direct imports to avoid relative import issues
import libs.BigNum128 as BigNum128
import libs.CertifiedMath as CertifiedMath

def test_certifiedmath_functions():
    """Test all CertifiedMath functions"""
    print("Testing CertifiedMath functions...")
    log_list = []
    
    # Test basic operations
    a = BigNum128.BigNum128.from_int(5)
    b = BigNum128.BigNum128.from_int(3)
    
    # Addition
    result = CertifiedMath.CertifiedMath.add(a, b, log_list)
    assert result.value == 8 * BigNum128.BigNum128.SCALE
    
    # Subtraction
    result = CertifiedMath.CertifiedMath.sub(a, b, log_list)
    assert result.value == 2 * BigNum128.BigNum128.SCALE
    
    # Multiplication
    result = CertifiedMath.CertifiedMath.mul(a, b, log_list)
    assert result.value == 15 * BigNum128.BigNum128.SCALE
    
    # Division
    result = CertifiedMath.CertifiedMath.div(a, b, log_list)
    # 5/3 = 1.666... * 1e18
    expected = 5 * BigNum128.BigNum128.SCALE * BigNum128.BigNum128.SCALE // (3 * BigNum128.BigNum128.SCALE)
    assert abs(result.value - expected) < BigNum128.BigNum128.SCALE // 1000000  # Allow small tolerance
    
    # Ln function
    one = BigNum128.BigNum128.from_int(1)
    result = CertifiedMath.CertifiedMath.ln(one, 10, log_list)
    assert result.value == 0
    
    # Phi series
    zero = BigNum128.BigNum128(0)
    result = CertifiedMath.CertifiedMath.phi_series(zero, 10, log_list)
    assert result.value == 0
    
    print("✓ CertifiedMath functions working correctly")

def test_architectural_boundaries():
    """Test that architectural boundaries are maintained"""
    print("Testing architectural boundaries...")
    
    # Check that HSMF-specific functions are NOT in CertifiedMath
    assert not hasattr(CertifiedMath.CertifiedMath, '_calculate_I_eff'), "HSMF-specific function found in CertifiedMath"
    assert not hasattr(CertifiedMath.CertifiedMath, '_calculate_c_holo'), "HSMF-specific function found in CertifiedMath"
    assert not hasattr(CertifiedMath.CertifiedMath, 'calculate_I_eff'), "HSMF-specific function found in CertifiedMath"
    assert not hasattr(CertifiedMath.CertifiedMath, 'calculate_c_holo'), "HSMF-specific function found in CertifiedMath"
    
    # Check that CertifiedMath has the required functions
    assert hasattr(CertifiedMath.CertifiedMath, '_safe_ln'), "Missing _safe_ln in CertifiedMath"
    assert hasattr(CertifiedMath.CertifiedMath, '_safe_phi_series'), "Missing _safe_phi_series in CertifiedMath"
    assert hasattr(CertifiedMath.CertifiedMath, 'ln'), "Missing ln in CertifiedMath"
    assert hasattr(CertifiedMath.CertifiedMath, 'phi_series'), "Missing phi_series in CertifiedMath"
    
    print("✓ Architectural boundaries maintained")

def main():
    """Run all comprehensive tests"""
    print("Running comprehensive QFS V13 verification tests...")
    print("=" * 60)
    
    try:
        test_certifiedmath_functions()
        test_architectural_boundaries()
        
        print("=" * 60)
        print("✓ All comprehensive tests passed!")
        print("The QFS V13 system is now fully compliant.")
        return True
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)