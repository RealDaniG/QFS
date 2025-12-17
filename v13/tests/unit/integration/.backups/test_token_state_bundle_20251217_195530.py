"""
Test to verify that TokenStateBundle works correctly with Zero-Simulation compliance.
"""
import json
try:
    from PQC import generate_keypair, sign_data
    from CertifiedMath import BigNum128
    from TokenStateBundle import TokenStateBundle, create_token_state_bundle, load_token_state_bundle
except ImportError:
    from PQC import generate_keypair, sign_data
    from CertifiedMath import BigNum128
    from TokenStateBundle import TokenStateBundle, create_token_state_bundle, load_token_state_bundle

def test_token_state_bundle_creation():
    """Test that TokenStateBundle can be created with proper parameters."""
    print('Testing TokenStateBundle creation...')
    chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99', 'token_balance': '1000.0'}
    flx_state = {'scaling_metric': '0.15', 'token_balance': '500.0'}
    psi_sync_state = {'frequency_metric': '0.08', 'token_balance': '750.0'}
    atr_state = {'directional_metric': '0.85', 'token_balance': '1200.0'}
    res_state = {'inertial_metric': '0.05', 'token_balance': '300.0'}
    lambda1 = BigNum128.from_string('1.618033988749894848')
    lambda2 = BigNum128.from_string('0.95')
    c_crit = BigNum128.from_string('0.95')
    bundle = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_BUNDLE_001', quantum_metadata={'source': 'test', 'timestamp': 1700000000})
    assert bundle.chr_state == chr_state
    assert bundle.flx_state == flx_state
    assert bundle.psi_sync_state == psi_sync_state
    assert bundle.atr_state == atr_state
    assert bundle.res_state == res_state
    assert bundle.pqc_cid == 'TEST_BUNDLE_001'
    assert bundle.lambda1.value == lambda1.value
    assert bundle.lambda2.value == lambda2.value
    assert bundle.c_crit.value == c_crit.value
    print('  [PASS] TokenStateBundle creation test passed')

def test_token_state_bundle_metrics():
    """Test that TokenStateBundle can retrieve metrics correctly."""
    print('Testing TokenStateBundle metrics retrieval...')
    chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99'}
    res_state = {'inertial_metric': '0.05'}
    flx_state = {'scaling_metric': '0.15'}
    psi_sync_state = {'frequency_metric': '0.08'}
    atr_state = {'directional_metric': '0.85'}
    lambda1 = BigNum128.from_string('1.618033988749894848')
    lambda2 = BigNum128.from_string('0.95')
    c_crit = BigNum128.from_string('0.95')
    bundle = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_BUNDLE_002')
    coherence_metric = bundle.get_coherence_metric()
    resonance_metric = bundle.get_resonance_metric()
    flux_metric = bundle.get_flux_metric()
    psi_sync_metric = bundle.get_psi_sync_metric()
    atr_metric = bundle.get_atr_metric()
    c_holo_proxy = bundle.get_c_holo_proxy()
    print(f'    Coherence metric: {coherence_metric.to_decimal_string()}')
    print(f'    Resonance metric: {resonance_metric.to_decimal_string()}')
    print(f'    Flux metric: {flux_metric.to_decimal_string()}')
    print(f'    Psi sync metric: {psi_sync_metric.to_decimal_string()}')
    print(f'    ATR metric: {atr_metric.to_decimal_string()}')
    print(f'    C_holo proxy: {c_holo_proxy.to_decimal_string()}')
    assert coherence_metric.to_decimal_string() == '0.980000000000000000'
    assert resonance_metric.to_decimal_string() == '0.050000000000000000'
    assert flux_metric.to_decimal_string() == '0.150000000000000000'
    assert psi_sync_metric.to_decimal_string() == '0.080000000000000000'
    assert atr_metric.to_decimal_string() == '0.850000000000000000'
    assert c_holo_proxy.to_decimal_string() == '0.990000000000000000'
    print('  [PASS] TokenStateBundle metrics retrieval test passed')

def test_survival_imperative():
    """Test that survival imperative check works correctly."""
    print('Testing survival imperative check...')
    chr_state = {'coherence_metric': '0.98'}
    res_state = {'inertial_metric': '0.05'}
    flx_state = {}
    psi_sync_state = {}
    atr_state = {}
    lambda1 = BigNum128.from_string('1.618033988749894848')
    lambda2 = BigNum128.from_string('0.95')
    c_crit = BigNum128.from_string('0.95')
    bundle = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_BUNDLE_003')
    assert bundle.check_survival_imperative() == True
    chr_state_low = {'coherence_metric': '0.90'}
    bundle_low = create_token_state_bundle(chr_state=chr_state_low, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_BUNDLE_004')
    assert bundle_low.check_survival_imperative() == False
    print('  [PASS] Survival imperative check test passed')

def test_deterministic_hashing():
    """Test that TokenStateBundle generates deterministic hashes."""
    print('Testing deterministic hashing...')
    chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99'}
    res_state = {'inertial_metric': '0.05'}
    flx_state = {'scaling_metric': '0.15'}
    psi_sync_state = {'frequency_metric': '0.08'}
    atr_state = {'directional_metric': '0.85'}
    lambda1 = BigNum128.from_string('1.618033988749894848')
    lambda2 = BigNum128.from_string('0.95')
    c_crit = BigNum128.from_string('0.95')
    bundle1 = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_BUNDLE_005', timestamp=1700000000)
    bundle2 = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_BUNDLE_005', timestamp=1700000000)
    hash1 = bundle1.get_deterministic_hash()
    hash2 = bundle2.get_deterministic_hash()
    assert hash1 == hash2
    assert len(hash1) == 64
    print('  [PASS] Deterministic hashing test passed')

def test_bundle_serialization():
    """Test that TokenStateBundle can be serialized and deserialized."""
    print('Testing bundle serialization...')
    chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99'}
    res_state = {'inertial_metric': '0.05'}
    flx_state = {'scaling_metric': '0.15'}
    psi_sync_state = {'frequency_metric': '0.08'}
    atr_state = {'directional_metric': '0.85'}
    lambda1 = BigNum128.from_string('1.618033988749894848')
    lambda2 = BigNum128.from_string('0.95')
    c_crit = BigNum128.from_string('0.95')
    bundle = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_BUNDLE_006')
    bundle_dict = bundle.to_dict()
    loaded_bundle = load_token_state_bundle(bundle_dict)
    assert loaded_bundle.chr_state == bundle.chr_state
    assert loaded_bundle.flx_state == bundle.flx_state
    assert loaded_bundle.psi_sync_state == bundle.psi_sync_state
    assert loaded_bundle.atr_state == bundle.atr_state
    assert loaded_bundle.res_state == bundle.res_state
    assert loaded_bundle.pqc_cid == bundle.pqc_cid
    assert loaded_bundle.lambda1.value == bundle.lambda1.value
    assert loaded_bundle.lambda2.value == bundle.lambda2.value
    assert loaded_bundle.c_crit.value == bundle.c_crit.value
    print('  [PASS] Bundle serialization test passed')

def test_pqc_signature_validation():
    """Test that PQC signature validation works correctly."""
    print('Testing PQC signature validation...')
    keypair = generate_keypair(pqc_cid='SIGNATURE_TEST_001')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    chr_state = {'coherence_metric': '0.98'}
    res_state = {'inertial_metric': '0.05'}
    flx_state = {}
    psi_sync_state = {}
    atr_state = {}
    lambda1 = BigNum128.from_string('1.618033988749894848')
    lambda2 = BigNum128.from_string('0.95')
    c_crit = BigNum128.from_string('0.95')
    bundle = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_BUNDLE_007')
    bundle_data = bundle.to_dict(include_signature=False)
    signature = sign_data(bundle_data, private_key, pqc_cid='SIGNATURE_TEST_002')
    bundle.signature = signature.hex()
    is_valid = bundle.validate_signature(public_key)
    assert is_valid == True
    bundle_invalid = create_token_state_bundle(chr_state={'coherence_metric': '0.90'}, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_BUNDLE_008')
    bundle_invalid.signature = signature.hex()
    is_valid_invalid = bundle_invalid.validate_signature(public_key)
    assert is_valid_invalid == False
    print('  [PASS] PQC signature validation test passed')

def run_all_tests():
    """Run all TokenStateBundle tests."""
    print('Running TokenStateBundle Tests...')
    print('=' * 40)
    test_token_state_bundle_creation()
    test_token_state_bundle_metrics()
    test_survival_imperative()
    test_deterministic_hashing()
    test_bundle_serialization()
    test_pqc_signature_validation()
    print('=' * 40)
    print('[SUCCESS] All TokenStateBundle tests passed!')
if __name__ == '__main__':
    run_all_tests()