from src.libs.BigNum128 import BigNum128

# Test underflow detection
print("Testing 0.0000000000000000100")
try:
    b = BigNum128.from_string("0.0000000000000000100")
    print(f"Success: {b.value}")
except Exception as e:
    print(f"Error: {e}")

# Test round-half-up
print("\nTesting 0.000000000000000005")
try:
    b = BigNum128.from_string("0.000000000000000005")
    print(f"Value: {b.value}")
except Exception as e:
    print(f"Error: {e}")

# Test integer + fraction
print("\nTesting 123.456789012345678")
try:
    b = BigNum128.from_string("123.456789012345678")
    print(f"Value: {b.value}")
    print(f"Expected: {123456789012345678}")
except Exception as e:
    print(f"Error: {e}")