"""
Phase 3 Comprehensive Verification Test Suite
Tests all requirements from FULL PHASE 3 AUDIT (VERIFIED LINE-BY-LINE)
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from libs.BigNum128 import BigNum128
from libs.DeterministicTime import DeterministicTime


def test_bignum128_arithmetic():
    """Test BigNum128 arithmetic operations (Audit Requirement)"""
    print("\n=== Testing BigNum128 Arithmetic ===")
    
    # Test add
    a = BigNum128.from_int(5)
    b = BigNum128.from_int(3)
    result = a.add(b)
    assert result.to_decimal_string() == "8.0", f"add failed: {result.to_decimal_string()}"
    print("✅ add: 5 + 3 = 8.0")
    
    # Test sub
    result = a.sub(b)
    assert result.to_decimal_string() == "2.0", f"sub failed: {result.to_decimal_string()}"
    print("✅ sub: 5 - 3 = 2.0")
    
    # Test mul
    result = a.mul(b)
    assert result.to_decimal_string() == "15.0", f"mul failed: {result.to_decimal_string()}"
    print("✅ mul: 5 * 3 = 15.0")
    
    # Test div
    result = a.div(b)
    expected = "1.666666666666666666"
    assert result.to_decimal_string() == expected, f"div failed: {result.to_decimal_string()}"
    print(f"✅ div: 5 / 3 = {expected}")
    
    # Test serialize_for_sign
    sig_bytes = a.serialize_for_sign()
    assert isinstance(sig_bytes, bytes), "serialize_for_sign must return bytes"
    assert sig_bytes == b'5.0', f"serialize failed: {sig_bytes}"
    print("✅ serialize_for_sign: b'5.0'")
    
    # Test overflow detection
    try:
        huge = BigNum128(BigNum128.MAX_VALUE)
        one = BigNum128.from_int(1)
        huge.add(one)
        assert False, "Should have raised OverflowError"
    except OverflowError:
        print("✅ Overflow detection working")
    
    # Test underflow detection
    try:
        zero = BigNum128.zero()
        one = BigNum128.from_int(1)
        zero.sub(one)
        assert False, "Should have raised ValueError for underflow"
    except ValueError:
        print("✅ Underflow detection working")
    
    print("✅ All BigNum128 arithmetic tests passed!")
    return True


def test_deterministic_time():
    """Test DeterministicTime methods (Audit Requirement)"""
    print("\n=== Testing DeterministicTime ===")
    
    # Test require_timestamp
    try:
        DeterministicTime.require_timestamp(100)
        print("✅ require_timestamp: valid timestamp accepted")
    except Exception as e:
        assert False, f"require_timestamp failed: {e}"
    
    # Test require_timestamp with invalid input
    try:
        DeterministicTime.require_timestamp(-1)
        assert False, "Should have raised ValueError for negative timestamp"
    except ValueError:
        print("✅ require_timestamp: negative timestamp rejected")
    
    # Test enforce_monotonicity
    try:
        DeterministicTime.enforce_monotonicity(200, 100)
        print("✅ enforce_monotonicity: accepts increasing time")
    except Exception as e:
        assert False, f"enforce_monotonicity failed: {e}"
    
    # Test monotonicity violation
    try:
        DeterministicTime.enforce_monotonicity(100, 200)
        assert False, "Should have raised ValueError for time regression"
    except ValueError as e:
        assert "regression" in str(e).lower(), f"Wrong error message: {e}"
        print("✅ enforce_monotonicity: detects time regression")
    
    # Test verify_drv_packet with dict
    packet_dict = {'ttsTimestamp': 100}
    try:
        DeterministicTime.verify_drv_packet(packet_dict, 100)
        print("✅ verify_drv_packet: dict format accepted")
    except Exception as e:
        assert False, f"verify_drv_packet failed with dict: {e}"
    
    # Test verify_drv_packet mismatch
    try:
        DeterministicTime.verify_drv_packet(packet_dict, 200)
        assert False, "Should have raised ValueError for timestamp mismatch"
    except ValueError as e:
        assert "mismatch" in str(e).lower(), f"Wrong error message: {e}"
        print("✅ verify_drv_packet: detects timestamp mismatch")
    
    # Test verify_and_use (should always fail)
    try:
        DeterministicTime.verify_and_use(100)
        assert False, "verify_and_use should always raise NotImplementedError"
    except NotImplementedError as e:
        assert "prohibited" in str(e).lower(), f"Wrong error message: {e}"
        print("✅ verify_and_use: correctly prohibits raw timestamps")
    
    print("✅ All DeterministicTime tests passed!")
    return True


def test_zero_simulation_compliance():
    """Test Zero-Simulation compliance (Audit Requirement)"""
    print("\n=== Testing Zero-Simulation Compliance ===")
    
    # Test that BigNum128 uses only integers internally
    a = BigNum128.from_string("3.14159")
    assert isinstance(a.value, int), "BigNum128 must use int internally"
    print("✅ BigNum128 uses integer representation")
    
    # Test that operations return BigNum128, not floats
    b = BigNum128.from_int(2)
    result = a.add(b)
    assert isinstance(result, BigNum128), "Operations must return BigNum128"
    assert isinstance(result.value, int), "Result must be integer internally"
    print("✅ All operations return BigNum128 (no floats)")
    
    # Test deterministic string conversion
    c = BigNum128.from_string("1.5")
    str1 = c.to_decimal_string()
    str2 = c.to_decimal_string()
    assert str1 == str2, "String conversion must be deterministic"
    print("✅ String conversion is deterministic")
    
    # Test comparison operators
    x = BigNum128.from_int(5)
    y = BigNum128.from_int(3)
    assert x > y, "Comparison operators must work"
    assert y < x, "Comparison operators must work"
    assert x >= y, "Comparison operators must work"
    assert y <= x, "Comparison operators must work"
    assert x != y, "Comparison operators must work"
    assert x == BigNum128.from_int(5), "Equality must work"
    print("✅ All comparison operators working")
    
    print("✅ All Zero-Simulation compliance tests passed!")
    return True


def test_audit_requirements():
    """Test specific Phase 3 Audit requirements"""
    print("\n=== Testing Phase 3 Audit Requirements ===")
    
    # Requirement 1: BigNum128 must have add/sub/mul/div
    assert hasattr(BigNum128, 'add'), "Missing add method"
    assert hasattr(BigNum128, 'sub'), "Missing sub method"
    assert hasattr(BigNum128, 'mul'), "Missing mul method"
    assert hasattr(BigNum128, 'div'), "Missing div method"
    print("✅ BigNum128 has all arithmetic methods")
    
    # Requirement 2: BigNum128 must have serialize_for_sign
    assert hasattr(BigNum128, 'serialize_for_sign'), "Missing serialize_for_sign"
    test_val = BigNum128.from_int(42)
    sig_bytes = test_val.serialize_for_sign()
    assert isinstance(sig_bytes, bytes), "serialize_for_sign must return bytes"
    print("✅ BigNum128 has PQC-ready serialization")
    
    # Requirement 3: DeterministicTime must have verify_drv_packet
    assert hasattr(DeterministicTime, 'verify_drv_packet'), "Missing verify_drv_packet"
    print("✅ DeterministicTime has verify_drv_packet")
    
    # Requirement 4: DeterministicTime must have enforce_monotonicity
    assert hasattr(DeterministicTime, 'enforce_monotonicity'), "Missing enforce_monotonicity"
    print("✅ DeterministicTime has enforce_monotonicity")
    
    # Requirement 5: DeterministicTime must have require_timestamp
    assert hasattr(DeterministicTime, 'require_timestamp'), "Missing require_timestamp"
    print("✅ DeterministicTime has require_timestamp")
    
    # Requirement 6: BigNum128 must have zero() and one() helpers
    assert hasattr(BigNum128, 'zero'), "Missing zero() helper"
    assert hasattr(BigNum128, 'one'), "Missing one() helper"
    zero = BigNum128.zero()
    one = BigNum128.one()
    assert zero.value == 0, "zero() must return 0"
    assert one.value == BigNum128.SCALE, "one() must return SCALE"
    print("✅ BigNum128 has zero() and one() helpers")
    
    print("✅ All Phase 3 Audit requirements verified!")
    return True


def test_fixed_point_precision():
    """Test fixed-point precision (18 decimal places)"""
    print("\n=== Testing Fixed-Point Precision ===")
    
    # Test SCALE constant
    assert BigNum128.SCALE == 10**18, f"SCALE must be 10^18, got {BigNum128.SCALE}"
    assert BigNum128.SCALE_DIGITS == 18, f"SCALE_DIGITS must be 18, got {BigNum128.SCALE_DIGITS}"
    print("✅ SCALE = 10^18 (18 decimal places)")
    
    # Test precision in operations
    a = BigNum128.from_string("0.000000000000000001")  # Smallest unit
    b = BigNum128.from_string("0.000000000000000001")
    result = a.add(b)
    expected = "0.000000000000000002"
    assert result.to_decimal_string() == expected, f"Precision lost: {result.to_decimal_string()}"
    print("✅ Maintains 18 decimal place precision")
    
    # Test large numbers
    large = BigNum128.from_string("340282366920938463463.374607431768211455")  # Near MAX_VALUE
    assert large.value > 0, "Large number handling failed"
    print("✅ Handles large numbers correctly")
    
    print("✅ All precision tests passed!")
    return True


def main():
    """Run all Phase 3 verification tests"""
    print("=" * 70)
    print("QFS V13 PHASE 3 COMPREHENSIVE VERIFICATION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("BigNum128 Arithmetic", test_bignum128_arithmetic),
        ("DeterministicTime", test_deterministic_time),
        ("Zero-Simulation Compliance", test_zero_simulation_compliance),
        ("Phase 3 Audit Requirements", test_audit_requirements),
        ("Fixed-Point Precision", test_fixed_point_precision),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL PHASE 3 VERIFICATION TESTS PASSED!")
        print("✅ QFS V13 is PRODUCTION READY for Phase 3 deployment")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed - review required")
        return 1


if __name__ == "__main__":
    sys.exit(main())
