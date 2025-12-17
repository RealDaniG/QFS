"""
Test script to verify RewardAllocator and TreasuryEngine fixes
"""
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum

def test_imports():
    """Test that imports work correctly"""
    from v13.libs.CertifiedMath import CertifiedMath, BigNum128
    from v13.core.reward_types import RewardBundle
    from v13.libs.governance.TreasuryEngine import TreasuryEngine
    from v13.libs.governance.RewardAllocator import RewardAllocator, AllocatedReward
    from v13.core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
    print('✓ All imports successful')

def test_deterministic_iteration():
    """Test that dictionary iteration is deterministic"""
    from v13.libs.CertifiedMath import CertifiedMath, BigNum128
    from v13.libs.governance.RewardAllocator import RewardAllocator
    cm = CertifiedMath()
    allocator = RewardAllocator(cm)
    weights = {'zebra': BigNum128.from_int(1), 'alpha': BigNum128.from_int(2), 'beta': BigNum128.from_int(3)}
    log_list = []
    normalized = allocator._normalize_weights(weights, log_list)
    keys = list(normalized.keys())
    assert keys == sorted(keys), f'Iteration order not deterministic: {keys}'
    print('✓ Deterministic iteration order verified')

def test_c_holo_check():
    """Test that C_holo < C_MIN check works"""
    from v13.libs.CertifiedMath import CertifiedMath, BigNum128, CertifiedMathError
    from v13.libs.governance.TreasuryEngine import TreasuryEngine
    from v13.core.TokenStateBundle import create_token_state_bundle
    cm = CertifiedMath()
    treasury = TreasuryEngine(cm)
    hsmf_metrics = {'S_CHR': BigNum128.from_int(5), 'C_holo': BigNum128.from_int(1), 'Action_Cost_QFS': BigNum128.from_int(2)}
    token_bundle = create_token_state_bundle(chr_state={'balance': '100.0', 'coherence_metric': '5.0'}, flx_state={'balance': '50.0', 'scaling_metric': '2.0'}, psi_sync_state={'balance': '25.0', 'frequency_metric': '1.0'}, atr_state={'balance': '30.0', 'directional_metric': '1.5'}, res_state={'balance': '40.0', 'inertial_metric': '2.5'}, nod_state={'balance': '10.0', 'reputation_metric': '5.0'}, lambda1=BigNum128.from_int(1), lambda2=BigNum128.from_int(1), c_crit=BigNum128.from_int(3), pqc_cid='test_treasury_001', timestamp=1234567890)
    log_list = []
    import pytest
    with pytest.raises(CertifiedMathError) as excinfo:
        treasury.calculate_rewards(hsmf_metrics=hsmf_metrics, token_bundle=token_bundle, log_list=log_list, pqc_cid='test_treasury_001', deterministic_timestamp=1234567890)
    assert 'C_holo < C_MIN' in str(excinfo.value), f'Wrong error message: {excinfo.value}'
    print('✓ C_holo < C_MIN check working correctly')

def main():
    """Run all tests"""
    print('Testing Reward System Fixes...')
    print('=' * 40)
    tests = [test_imports, test_deterministic_iteration, test_c_holo_check]
    passed = 0
    for test in tests:
        if test():
            passed += 1
    print('=' * 40)
    print(f'Tests passed: {passed}/{len(tests)}')
    if passed == len(tests):
        print('🎉 All tests passed! Reward system is QFS V13.5 compliant.')
        return True
    else:
        print('❌ Some tests failed. Please review the fixes.')
        return False
if __name__ == '__main__':
    success = main()
    raise ZeroSimAbort(0 if success else 1)