from CertifiedMath import CertifiedMath, BigNum128
from HSMF import HSMF, ValidationResult
from TokenStateBundle import create_token_state_bundle, TokenStateBundle
import json

def test_hsmf_tokenstate_integration():
    """Comprehensive test for HSMF and TokenStateBundle integration."""
    print('=== HSMF and TokenStateBundle Integration Test ===')
    bundle_creation_success = False
    validation_success = False
    validation_passed = False
    serialization_success = False
    all_keys_present = False
    deterministic_creation = False
    print('\n1. Testing token state bundle creation...')
    timestamp = 1700000000
    chr_state = {'resonance_freq': BigNum128.from_string('432.000000000000000000'), 'amplitude': BigNum128.from_string('0.750000000000000000'), 'phase': BigNum128.from_string('1.570796326794896619'), 'coherence_metric': BigNum128.from_string('1.500000000000000000')}
    flx_state = {'flux_rate': BigNum128.from_string('0.025000000000000000'), 'volatility': BigNum128.from_string('0.150000000000000000'), 'momentum': BigNum128.from_string('0.800000000000000000')}
    psi_sync_state = {'sync_factor': BigNum128.from_string('0.950000000000000000'), 'coherence': BigNum128.from_string('0.880000000000000000'), 'stability': BigNum128.from_string('0.920000000000000000')}
    atr_state = {'attraction_level': BigNum128.from_string('0.700000000000000000'), 'attraction_potential': BigNum128.from_string('1.200000000000000000'), 'attraction_field': BigNum128.from_string('0.850000000000000000'), 'directional_metric': BigNum128.from_string('0.001000000000000000'), 'atr_magnitude': BigNum128.from_string('1.000000000000000000')}
    res_state = {'resonance_level': BigNum128.from_string('0.650000000000000000'), 'resonance_potential': BigNum128.from_string('1.100000000000000000'), 'resonance_field': BigNum128.from_string('0.780000000000000000')}
    lambda1 = BigNum128.from_string('0.500000000000000000')
    lambda2 = BigNum128.from_string('0.300000000000000000')
    c_crit = BigNum128.from_string('1.000000000000000000')
    pqc_cid = 'QFSV13-HSMF-TEST-001'
    quantum_metadata = {'test_suite': 'integration', 'entropy_source': 'deterministic', 'validation_level': 'full'}
    bundle_id = 'test-bundle-001'
    f_atr = BigNum128.from_string('0.000010000000000000')
    try:
        token_bundle = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, lambda1, lambda2, c_crit, pqc_cid, timestamp, quantum_metadata, bundle_id)
        bundle_creation_success = True
        print(f'  Token bundle created successfully')
        print(f'  Bundle ID: {token_bundle.bundle_id}')
        print(f'  Timestamp: {token_bundle.timestamp}')
        print(f'  PQC CID: {token_bundle.pqc_cid}')
    except Exception as e:
        bundle_creation_success = False
        print(f'  Bundle creation failed: {e}')
    print('\n2. Testing HSMF validation of token bundle...')
    if bundle_creation_success:
        log_list = []
        cm = CertifiedMath(log_list)
        hsmf = HSMF(cm)
        try:
            validation_result = hsmf.validate_action_bundle(token_bundle, f_atr, pqc_cid, raise_on_failure=False, strict_atr_coherence=True, quantum_metadata=quantum_metadata)
            validation_success = isinstance(validation_result, ValidationResult)
            validation_passed = validation_result.is_valid if validation_success else False
            print(f'  Validation executed successfully: {validation_success}')
            print(f'  Validation passed: {validation_passed}')
            if validation_success:
                print(f'  Validation message: {validation_result.errors}')
                print(f"  Coherence metric: {(validation_result.raw_metrics.get('s_chr', 'N/A').to_decimal_string() if 's_chr' in validation_result.raw_metrics else 'N/A')}")
        except Exception as e:
            validation_success = False
            validation_passed = False
            print(f'  Validation failed with exception: {e}')
    else:
        validation_success = False
        validation_passed = False
        print('  Skipping validation due to bundle creation failure')
    print('\n3. Testing bundle serialization...')
    if bundle_creation_success:
        try:
            serialized_bundle = token_bundle.to_dict()
            serialization_success = True
            print(f'  Serialization successful')
            print(f'  Serialized bundle keys: {list(serialized_bundle.keys())}')
            required_keys = ['bundle_id', 'timestamp', 'pqc_cid', 'chr_state', 'flx_state', 'psi_sync_state', 'atr_state', 'res_state', 'lambda1', 'lambda2', 'c_crit']
            all_keys_present = all((key in serialized_bundle for key in required_keys))
            print(f'  All required keys present: {all_keys_present}')
        except Exception as e:
            serialization_success = False
            all_keys_present = False
            print(f'  Serialization failed: {e}')
    else:
        serialization_success = False
        all_keys_present = False
        print('  Skipping serialization due to bundle creation failure')
    print('\n5. Testing deterministic behavior...')
    try:
        token_bundle1 = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, lambda1, lambda2, c_crit, pqc_cid, timestamp, quantum_metadata, 'test-bundle-002')
        token_bundle2 = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, lambda1, lambda2, c_crit, pqc_cid, timestamp, quantum_metadata, 'test-bundle-003')
        deterministic_creation = token_bundle1.chr_state['resonance_freq'].value == token_bundle2.chr_state['resonance_freq'].value and token_bundle1.flx_state['flux_rate'].value == token_bundle2.flx_state['flux_rate'].value and (token_bundle1.psi_sync_state['sync_factor'].value == token_bundle2.psi_sync_state['sync_factor'].value) and (token_bundle1.atr_state['attraction_level'].value == token_bundle2.atr_state['attraction_level'].value) and (token_bundle1.res_state['resonance_level'].value == token_bundle2.res_state['resonance_level'].value) and (token_bundle1.lambda1.value == token_bundle2.lambda1.value) and (token_bundle1.lambda2.value == token_bundle2.lambda2.value) and (token_bundle1.c_crit.value == token_bundle2.c_crit.value)
        print(f'  Deterministic bundle creation: {deterministic_creation}')
    except Exception as e:
        deterministic_creation = False
        print(f'  Deterministic behavior test failed: {e}')
    print('\n=== Integration Test Summary ===')
    all_tests_passed = bundle_creation_success and validation_success and validation_passed and serialization_success and all_keys_present and deterministic_creation
    print(f'All integration tests passed: {all_tests_passed}')
    return all_tests_passed
if __name__ == '__main__':
    test_hsmf_tokenstate_integration()