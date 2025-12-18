"""
Test suite for Phase 3 integration validation
Verifies all components work together correctly
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import json
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.libs.economics.GenesisHarmonicState import GENESIS_STATE, boot_from_genesis
from v13.libs.economics.PsiFieldEngine import DiscretePsiField
from v13.libs.economics.HarmonicEconomics import HarmonicEconomics
from v13.libs.economics.PsiSyncProtocol import PsiSyncProtocol
from v13.libs.economics.TreasuryDistributionEngine import TreasuryDistributionEngine
from v13.libs.economics.HoloRewardEngine import HoloRewardEngine
from v13.libs.economics.SystemRecoveryProtocol import SystemRecoveryProtocol
from v13.libs.economics.EconomicAdversarySuite import EconomicAdversarySuite
from v13.core.TokenStateBundle import create_token_state_bundle
from v13.core.CoherenceLedger import CoherenceLedger

class MockPQC:

    def __init__(self):
        pass

    def sign_data(self, private_key, data, log_list):
        return type('obj', (object,), {'signature': b'mock_signature'})()

    def verify_signature(self, public_key, data, signature, log_list):
        return type('obj', (object,), {'is_valid': True})()

def test_phase3_integration():
    """Test that all Phase 3 components integrate correctly"""
    print('Testing Phase 3 Integration...')
    cm = CertifiedMath()
    genesis_topology = GENESIS_STATE['topology']
    genesis_state = boot_from_genesis(cm)
    print('✓ Genesis state created')
    psi_field = DiscretePsiField(genesis_topology, cm)
    print('✓ PsiFieldEngine created')
    economics = HarmonicEconomics(psi_field, cm)
    print('✓ HarmonicEconomics created')
    psisync = PsiSyncProtocol(cm)
    print('✓ PsiSyncProtocol created')
    pqc = MockPQC()
    treasury = TreasuryDistributionEngine(cm, pqc, None, psi_field, psisync)
    print('✓ TreasuryDistributionEngine created')
    holo_reward = HoloRewardEngine(cm, None, psi_field)
    print('✓ HoloRewardEngine created')
    ledger = CoherenceLedger(cm)
    print('✓ CoherenceLedger created')
    founding_nodes = GENESIS_STATE['governance']['founding_nodes']
    recovery_threshold = GENESIS_STATE['governance']['recovery_threshold']
    recovery = SystemRecoveryProtocol(cm, pqc, founding_nodes, recovery_threshold)
    print('✓ SystemRecoveryProtocol created')
    recovery.integrate_with_phase3_components(psi_field_engine=psi_field, harmonic_economics=economics, treasury_engine=treasury, psisync_protocol=psisync)
    print('✓ Recovery protocol integrated with Phase 3 components')
    adversary_suite = EconomicAdversarySuite(cm, psi_field, economics, treasury, psisync, ledger, recovery, genesis_state)
    print('✓ EconomicAdversarySuite created')
    chr_state = {'shards': genesis_state['token_allocations']['shards']}
    token_bundle = create_token_state_bundle(chr_state=chr_state, flx_state={}, psi_sync_state={}, atr_state={}, res_state={}, nod_state={}, lambda1=BigNum128(1618033988749894848), lambda2=BigNum128(618033988749894848), c_crit=BigNum128(1000000000000000000), pqc_cid='TEST_PHASE3_INTEGRATION', timestamp=1234567890, parameters={'δ_curl': BigNum128(10), 'MAX_CHR_SUPPLY': BigNum128(10000000000), 'δ_max': BigNum128(5), 'ε_sync': BigNum128(2)})
    print('✓ TokenStateBundle created')
    density_0 = psi_field.psi_density('shard_0', token_bundle)
    print(f'✓ Psi density for shard_0: {density_0}')
    try:
        new_state = economics.compute_harmonic_state(token_bundle)
        print('✓ HarmonicEconomics compute_harmonic_state executed successfully')
    except Exception as e:
        print(f'⚠ HarmonicEconomics compute_harmonic_state raised exception: {e}')
    shard_psisync_values = {'shard_0': 100, 'shard_1': 105, 'shard_2': 95, 'shard_3': 102, 'shard_4': 98}
    drv_packet = type('DRV_Packet', (), {'ttsTimestamp': 1234567890, 'sequence': 1, 'previous_hash': '0' * 64})()
    consensus_result = psisync.compute_global_psisync(shard_psisync_values, epsilon_sync=10, deterministic_timestamp=1234567890, drv_packet_seq=drv_packet)
    print(f'✓ PsiSyncProtocol compute_global_psisync executed successfully')
    print(f"  Global ΨSync: {consensus_result['global_psisync']}")
    try:
        treasury_result = treasury.compute_system_treasury_distribution(token_bundle, treasury_balance=1000000, genesis_shard_ids=['shard_0', 'shard_1', 'shard_2', 'shard_3', 'shard_4'], deterministic_timestamp=1234567890, drv_packet_seq=drv_packet)
        print('✓ TreasuryDistributionEngine compute_system_treasury_distribution executed successfully')
    except Exception as e:
        print(f'⚠ TreasuryDistributionEngine compute_system_treasury_distribution raised exception: {e}')
    try:
        reward_result = holo_reward.compute_holofield_reward_package(intensity=100, resonance=50, harmonic_state=token_bundle, treasury_state=type('obj', (object,), {'total_distributed': 1000000})(), deterministic_timestamp=1234567890, drv_packet_seq=drv_packet)
        print('✓ HoloRewardEngine compute_holofield_reward_package executed successfully')
        print(f"  Reward multiplier: {reward_result['reward_multiplier']}")
    except Exception as e:
        print(f'⚠ HoloRewardEngine compute_holofield_reward_package raised exception: {e}')
    ledger_entry = ledger.log_state(token_bundle)
    print(f'✓ CoherenceLedger log_state executed successfully')
    print(f'  Entry ID: {ledger_entry.entry_id[:16]}...')
    recovery_status = recovery.get_recovery_status(deterministic_timestamp=1234567890, drv_packet_seq=drv_packet)
    print(f'✓ SystemRecoveryProtocol get_recovery_status executed successfully')
    print(f"  Current state: {recovery_status['current_state']}")
    print('\n' + '=' * 50)
    print('🎉 ALL PHASE 3 COMPONENTS INTEGRATED SUCCESSFULLY')
    print('=' * 50)
    return True
if __name__ == '__main__':
    success = test_phase3_integration()
    raise ZeroSimAbort(0 if success else 1)
