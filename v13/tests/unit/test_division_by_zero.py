from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128
cm = CertifiedMath()
log_list = []
try:
    result = cm.div(BigNum128(1), BigNum128(0), log_list)
    print('Failed - should have raised ZeroDivisionError')
    raise ZeroSimAbort(1)
except ZeroDivisionError:
    print('✓ Correctly raised ZeroDivisionError for division by zero')
except Exception as e:
    print(f'Unexpected error: {e}')
    raise ZeroSimAbort(1)