import sys

from CertifiedMath import CertifiedMath, BigNum128, MathOverflowError

def test_proper_overflow():
    """Test proper overflow behavior."""
    cm = CertifiedMath([])
    
    # Create values that will definitely cause overflow
    # MAX_VALUE is 2^127 - 1 = 170141183460469231731687303715884105727
    max_val = BigNum128(BigNum128.MAX_VALUE)
    increment = BigNum128(BigNum128.SCALE)  # 1.0
    
    print(f"Max value: {max_val.to_decimal_string()}")
    print(f"Increment: {increment.to_decimal_string()}")
    
    try:
        result = cm.add(max_val, increment, "overflow_test", {"test": "overflow"})
        print(f"Result: {result.to_decimal_string()}")
        print("No overflow occurred - this is unexpected")
        return False
    except MathOverflowError as e:
        print(f"Overflow correctly caught: {e}")
        return True
    except Exception as e:
        print(f"Other error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_proper_overflow()
    print(f"Overflow test passed: {success}")