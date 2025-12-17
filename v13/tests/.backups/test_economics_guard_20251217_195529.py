"""
Simple test to verify EconomicsGuard functionality
"""
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
from v13.libs.economics.EconomicsGuard import EconomicsGuard
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

def test_economics_guard():
    """Test the EconomicsGuard implementation."""
    print('Testing EconomicsGuard...')
    cm = CertifiedMath()
    economics_guard = EconomicsGuard(cm)
    log_list = []
    reward_amount = BigNum128.from_int(100)
    current_daily_total = BigNum128.from_int(1000)
    current_total_supply = BigNum128.from_int(100000)
    result1 = economics_guard.validate_chr_reward(reward_amount=reward_amount, current_daily_total=current_daily_total, current_total_supply=current_total_supply, log_list=log_list)
    print(f'Valid CHR reward validation: {result1.passed}')
    if not result1.passed:
        print(f'Error code: {result1.error_code}')
        print(f'Error message: {result1.error_message}')
    high_reward_amount = BigNum128.from_int(100000)
    result2 = economics_guard.validate_chr_reward(reward_amount=high_reward_amount, current_daily_total=current_daily_total, current_total_supply=current_total_supply, log_list=log_list)
    print(f'High CHR reward validation: {result2.passed}')
    if not result2.passed:
        print(f'Error code: {result2.error_code}')
        print(f'Error message: {result2.error_message}')
    if result1.passed and (not result2.passed):
        print('✅ ECONOMICS GUARD TEST PASSED!')
        return True
    else:
        print('❌ ECONOMICS GUARD TEST FAILED!')
        return False
if __name__ == '__main__':
    success = test_economics_guard()
    raise ZeroSimAbort(0 if success else 1)