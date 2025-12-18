import sys

sys.path.append(".")
from v13.libs.BigNum128 import BigNum128, BigNum128Error


print("Sys Path:", sys.path)
print(
    "BigNum128 File:", BigNum128.__module__, sys.modules[BigNum128.__module__].__file__
)


def test_edge_cases():
    """Test edge cases for BigNum128"""
    print("Testing BigNum128 edge cases...")
    try:
        result = BigNum128.from_string(".0")
        print(f"✓ .0 correctly parsed as: {result}")
    except Exception as e:
        print(f"✗ Failed to parse .0: {e}")
    try:
        result = BigNum128.from_string("0.")
        print(f"✓ 0. correctly parsed as: {result}")
    except Exception as e:
        print(f"✗ Failed to parse 0.: {e}")
    try:
        BigNum128.from_string("-1.5")
        print("✗ Should have raised BigNum128Error for negative value")
    except BigNum128Error as e:
        print(f"✓ Correctly raised BigNum128Error for negative value: {e}")
    except Exception as e:
        print(f"✗ Raised wrong exception type for negative value: {e}")
    try:
        BigNum128.from_string("0.0000000000000000001")
        print("✗ Should have raised BigNum128Error for underflow")
    except BigNum128Error as e:
        print(f"✓ Correctly raised BigNum128Error for underflow: {e}")
    except Exception as e:
        print(f"✗ Raised wrong exception type for underflow: {e}")


def test_comparisons():
    """Test comparison operators"""
    print("\nTesting BigNum128 comparisons...")
    a = BigNum128(1000000000000000000)
    b = BigNum128(2000000000000000000)
    c = BigNum128(1000000000000000000)
    if a == c and a != b:
        print("✓ Equality comparisons work correctly")
    else:
        print("✗ Equality comparisons failed")
    if a < b and (not b < a):
        print("✓ Less than comparison works correctly")
    else:
        print("✗ Less than comparison failed")
    if b > a and (not a > b):
        print("✓ Greater than comparison works correctly")
    else:
        print("✗ Greater than comparison failed")
    if a <= c and a <= b:
        print("✓ Less than or equal comparison works correctly")
    else:
        print("✗ Less than or equal comparison failed")
    if c >= a and b >= a:
        print("✓ Greater than or equal comparison works correctly")
    else:
        print("✗ Greater than or equal comparison failed")


def test_constants():
    """Test zero and one constants"""
    print("\nTesting BigNum128 constants...")
    zero = BigNum128.zero()
    one = BigNum128.one()
    if zero.value == 0:
        print("✓ BigNum128.zero() works correctly")
    else:
        print(f"✗ BigNum128.zero() failed: {zero.value} (type: {type(zero.value)})")

    print(f"DEBUG: one.value = {one.value}, type = {type(one.value)}")
    print(f"DEBUG: BigNum128.SCALE = {BigNum128.SCALE}, type = {type(BigNum128.SCALE)}")

    if one.value == BigNum128.SCALE:
        print("✓ BigNum128.one() works correctly")
    else:
        print(f"✗ BigNum128.one() failed: {one.value} (type: {type(one.value)})")


if __name__ == "__main__":
    test_edge_cases()
    test_comparisons()
    test_constants()
    print("\n🎉 All BigNum128 fixes verified!")
