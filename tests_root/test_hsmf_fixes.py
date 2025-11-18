import sys
import os

# Add the src directory to the path so we can import HSMF
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hsmf_constants():
    """Test that HSMF constants are correctly defined"""
    try:
        from core.HSMF import HSMF
        from libs.CertifiedMath import CertifiedMath, BigNum128
        
        # Create a mock CertifiedMath instance
        cm = CertifiedMath()
        
        # Create HSMF instance
        hsmf = HSMF(cm)
        
        print("Testing HSMF constants...")
        
        # Test ONE constant
        assert hsmf.ONE.value == BigNum128.from_int(1).value, f"ONE constant incorrect: {hsmf.ONE.value}"
        print(f"✅ ONE constant: {hsmf.ONE.to_decimal_string()}")
        
        # Test ZERO constant
        assert hsmf.ZERO.value == BigNum128.from_int(0).value, f"ZERO constant incorrect: {hsmf.ZERO.value}"
        print(f"✅ ZERO constant: {hsmf.ZERO.to_decimal_string()}")
        
        # Test ONE_PERCENT constant
        expected_one_percent = BigNum128(10000000000000000)  # 0.01 * 10^18
        assert hsmf.ONE_PERCENT.value == expected_one_percent.value, f"ONE_PERCENT constant incorrect: {hsmf.ONE_PERCENT.value}"
        print(f"✅ ONE_PERCENT constant: {hsmf.ONE_PERCENT.to_decimal_string()}")
        
        # Test PHI constant
        expected_phi = BigNum128(1618033988749894848)  # φ (golden ratio) * 1e18
        assert hsmf.PHI.value == expected_phi.value, f"PHI constant incorrect: {hsmf.PHI.value}"
        print(f"✅ PHI constant: {hsmf.PHI.to_decimal_string()}")
        
        print("✅ All HSMF constants verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing HSMF constants: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hsmf_imports():
    """Test that HSMF imports are correct"""
    try:
        from core.HSMF import HSMF, ValidationResult
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from handlers.CIR302_Handler import CIR302_Handler
        
        print("✅ HSMF imports verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing HSMF imports: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_hsmf_imports()
    success2 = test_hsmf_constants()
    
    if success1 and success2:
        print("\n🎉 All HSMF fixes verified successfully!")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)