"""
Comprehensive test to verify all modules are working together correctly.
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

def test_all_modules():
    """Test all modules to ensure they work together."""
    print('Running comprehensive test of all QFS V13 modules...')
    try:
        from src.libs.CertifiedMath import CertifiedMath, BigNum128
        print('✓ CertifiedMath imported successfully')
        from src.libs.PQC import PQC
        print('✓ PQC imported successfully')
        from src.core.TokenStateBundle import TokenStateBundle
        print('✓ TokenStateBundle imported successfully')
        from src.libs.governance.TreasuryEngine import TreasuryEngine
        print('✓ TreasuryEngine imported successfully')
        from src.libs.governance.RewardAllocator import RewardAllocator, AllocatedReward
        print('✓ RewardAllocator imported successfully')
        from src.libs.integration.StateTransitionEngine import StateTransitionEngine
        print('✓ StateTransitionEngine imported successfully')
        from src.libs.integration.HolonetSync import HolonetSync
        print('✓ HolonetSync imported successfully')
        from src.libs.core.UtilityOracle import UtilityOracle
        print('✓ UtilityOracle imported successfully')
        from src.libs.quantum.QPU_Interface import QPU_Interface
        print('✓ QPU_Interface imported successfully')
        from src.handlers.CIR302_Handler import CIR302_Handler
        print('✓ CIR302_Handler imported successfully')
        cm = CertifiedMath()
        print('✓ CertifiedMath instance created successfully')
        a = BigNum128.from_int(100)
        b = BigNum128.from_int(50)
        with cm.LogContext() as log_list:
            result = cm.add(a, b, log_list)
            print(f'✓ Basic math operation: 100 + 50 = {result.to_decimal_string()}')
            treasury = TreasuryEngine(cm)
            print('✓ TreasuryEngine instance created successfully')
            allocator = RewardAllocator(cm)
            print('✓ RewardAllocator instance created successfully')
            state_engine = StateTransitionEngine(cm)
            print('✓ StateTransitionEngine instance created successfully')
            holonet = HolonetSync(cm)
            print('✓ HolonetSync instance created successfully')
            oracle = UtilityOracle(cm)
            print('✓ UtilityOracle instance created successfully')
            qpu = QPU_Interface(cm)
            print('✓ QPU_Interface instance created successfully')
            atr_state = BigNum128.from_int(50)
            guidance = oracle.get_atr_directional_vector(current_atr_state=atr_state, log_list=log_list, pqc_cid='test_001', deterministic_timestamp=1234567890)
            print(f'✓ UtilityOracle guidance calculation: {guidance.to_decimal_string()}')
            entropy = qpu.get_quantum_entropy(length=16, log_list=log_list, pqc_cid='test_001', deterministic_timestamp=1234567890)
            print(f'✓ QPU_Interface entropy generation: {len(entropy.raw_entropy)} bytes')
            sync_result = holonet.propagate_finality(bundle_hash='test_bundle_123', log_hash='test_log_456', coherence_metrics={'c_holo': '0.95', 's_chr': '0.98'}, log_list=log_list, pqc_cid='test_001', deterministic_timestamp=1234567890)
            print(f'✓ HolonetSync propagation: {sync_result}')
        print('\n✅ All modules imported and basic functionality tested successfully!')
        print(f'✅ Total log entries generated: {len(log_list)}')
        return True
    except Exception as e:
        print(f'❌ Error testing modules: {e}')
        import traceback
        traceback.print_exc()
        return False
if __name__ == '__main__':
    success = test_all_modules()
    raise ZeroSimAbort(0 if success else 1)
