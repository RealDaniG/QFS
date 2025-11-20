from libs.BigNum128 import BigNum128

try:
    BigNum128.from_string('-1.5')
    print('Failed - should have raised ValueError')
except ValueError as e:
    print(f'✓ Correctly rejected negative values: {e}')
except Exception as e:
    print(f'Unexpected error: {e}')