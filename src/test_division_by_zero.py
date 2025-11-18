import sys
from libs.CertifiedMath import CertifiedMath
from libs.BigNum128 import BigNum128

# Create a log list for the operations
log_list = []

try:
    result = CertifiedMath.div(BigNum128(1), BigNum128(0), log_list)
    print('Failed - should have raised ZeroDivisionError')
    sys.exit(1)
except ZeroDivisionError:
    print('✓ Correctly raised ZeroDivisionError for division by zero')
except Exception as e:
    print(f'Unexpected error: {e}')
    sys.exit(1)