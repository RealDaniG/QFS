from v13.libs.BigNum128 import BigNum128
try:
    BigNum128.from_string('0.0000000000000000001')
    print('Failed - should have raised ValueError')
except ValueError:
    print('✓ Correctly rejected too-small underflow')
except Exception as e:
    print(f'Unexpected error: {e}')
