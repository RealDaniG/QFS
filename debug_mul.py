from src.libs.BigNum128 import BigNum128

# Test multiplication overflow
max_val = BigNum128(BigNum128.MAX_VALUE)
two = BigNum128(2 * BigNum128.SCALE)

try:
    result = max_val.mul(two)
    print(f"Result: {result.value}")
except OverflowError as e:
    print(f"Caught OverflowError: {e}")