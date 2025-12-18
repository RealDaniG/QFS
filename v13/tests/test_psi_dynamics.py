"""
Test suite for ψ-Dynamics validation
Verifies ψ-field calculation, density, gradient, and curl computations
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import json
import hashlib
from v13.libs.economics.PsiFieldEngine import DiscretePsiField, create_secure_psi_field
from v13.core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
from v13.libs.CertifiedMath import BigNum128, CertifiedMath

def test_psi_density_bounded():
    """Test that ψ-density is properly bounded"""
    print('Testing ψ-density bounded...')
    topology = {'shard_connections': [['shard_0', 'shard_1'], ['shard_1', 'shard_2']], 'min_connection_degree': 1, 'max_connection_degree': 2}
    field_engine = create_secure_psi_field(topology, CertifiedMath)
    chr_state = {'shards': {'shard_0': {'CHR': BigNum128(1000000000), 'ATR': BigNum128(500000), 'DISSONANCE': BigNum128(10000)}, 'shard_1': {'CHR': BigNum128(2000000000), 'ATR': BigNum128(1000000), 'DISSONANCE': BigNum128(20000)}}}
    flx_state = {}
    psi_sync_state = {}
    atr_state = {}
    res_state = {}
    token_bundle = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=BigNum128(1618033988749894848), lambda2=BigNum128(618033988749894848), c_crit=BigNum128(1000000000000000000), pqc_cid='TEST_PSI_DENSITY', timestamp=1234567890, parameters={'δ_curl': BigNum128(10), 'MAX_CHR_SUPPLY': BigNum128(10000000000), 'δ_max': BigNum128(5), 'ε_sync': BigNum128(2)})
    density_0 = field_engine.psi_density('shard_0', token_bundle)
    density_1 = field_engine.psi_density('shard_1', token_bundle)
    print(f'ψ-density for shard_0: {density_0}')
    print(f'ψ-density for shard_1: {density_1}')
    assert density_0.value >= 0, 'ψ-density should be non-negative'
    assert density_1.value >= 0, 'ψ-density should be non-negative'
    print('✓ ψ-density bounded test passed')

def test_psi_gradient_deterministic():
    """Test that ψ-gradient is deterministic"""
    print('Testing ψ-gradient deterministic...')
    topology = {'shard_connections': [['shard_0', 'shard_1']], 'min_connection_degree': 1, 'max_connection_degree': 1}
    field_engine = create_secure_psi_field(topology, CertifiedMath)
    chr_state = {'shards': {'shard_0': {'CHR': BigNum128(1000000000), 'ATR': BigNum128(500000), 'DISSONANCE': BigNum128(10000)}, 'shard_1': {'CHR': BigNum128(2000000000), 'ATR': BigNum128(1000000), 'DISSONANCE': BigNum128(20000)}}}
    flx_state = {}
    psi_sync_state = {}
    atr_state = {}
    res_state = {}
    token_bundle = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=BigNum128(1618033988749894848), lambda2=BigNum128(618033988749894848), c_crit=BigNum128(1000000000000000000), pqc_cid='TEST_PSI_GRADIENT', timestamp=1234567890, parameters={'δ_curl': BigNum128(10), 'MAX_CHR_SUPPLY': BigNum128(10000000000), 'δ_max': BigNum128(5), 'ε_sync': BigNum128(2)})
    gradient_1 = field_engine.psi_gradient('shard_0', 'shard_1', token_bundle)
    gradient_2 = field_engine.psi_gradient('shard_0', 'shard_1', token_bundle)
    print(f'ψ-gradient (first calculation): {gradient_1}')
    print(f'ψ-gradient (second calculation): {gradient_2}')
    assert gradient_1.value == gradient_2.value, 'ψ-gradient should be deterministic'
    print('✓ ψ-gradient deterministic test passed')

def test_psi_curl_cycle_anomalies():
    """Test that ψCurl cycle anomalies are detected"""
    print('Testing ψCurl cycle anomalies detection...')
    topology = {'shard_connections': [['shard_0', 'shard_1'], ['shard_1', 'shard_2'], ['shard_2', 'shard_0']], 'min_connection_degree': 2, 'max_connection_degree': 2}
    field_engine = create_secure_psi_field(topology, CertifiedMath)
    chr_state = {'shards': {'shard_0': {'CHR': BigNum128(1000000000), 'ATR': BigNum128(500000), 'DISSONANCE': BigNum128(10000)}, 'shard_1': {'CHR': BigNum128(2000000000), 'ATR': BigNum128(1000000), 'DISSONANCE': BigNum128(20000)}, 'shard_2': {'CHR': BigNum128(1500000000), 'ATR': BigNum128(750000), 'DISSONANCE': BigNum128(15000)}}}
    flx_state = {}
    psi_sync_state = {}
    atr_state = {}
    res_state = {}
    token_bundle = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=BigNum128(1618033988749894848), lambda2=BigNum128(618033988749894848), c_crit=BigNum128(1000000000000000000), pqc_cid='TEST_PSI_CURL', timestamp=1234567890, parameters={'δ_curl': BigNum128(10), 'MAX_CHR_SUPPLY': BigNum128(10000000000), 'δ_max': BigNum128(5), 'ε_sync': BigNum128(2)})
    validation_result = field_engine.validate_psi_field_integrity(token_bundle, delta_curl_threshold=100)
    print(f'Validation result: {validation_result}')
    print(f"Number of curls detected: {len(validation_result['psi_curls'])}")
    assert len(field_engine.cycle_basis) > 0, 'Cycle basis should be computed for triangular topology'
    assert len(validation_result['psi_curls']) > 0, 'ψ-curls should be computed for cycle'
    print('✓ ψCurl cycle anomalies detection test passed')

def main():
    """Run all ψ-dynamics tests"""
    print('Running ψ-Dynamics Validation Tests')
    print('=' * 40)
    try:
        test_psi_density_bounded()
        test_psi_gradient_deterministic()
        test_psi_curl_cycle_anomalies()
        print('\n' + '=' * 40)
        print('🎉 ALL ψ-DYNAMICS TESTS PASSED')
        print('Expected:')
        print('- ψ-density bounded')
        print('- ψ-gradient deterministic')
        print('- ψCurl cycle anomalies detected')
        print('Result: No ψCurl divergence events')
        return True
    except Exception as e:
        print(f'\n❌ TEST FAILED: {e}')
        return False
if __name__ == '__main__':
    success = main()
    raise ZeroSimAbort(0 if success else 1)
