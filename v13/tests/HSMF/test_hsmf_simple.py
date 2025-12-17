"""
Simple test file to verify HSMF.py structure and method signatures
"""
from CertifiedMath import BigNum128, CertifiedMath

def test_hsmf_structure():
    """Test that HSMF.py has the correct structure and method signatures"""
    print('Testing HSMF structure and method signatures...')
    try:
        from HSMF import HSMF
        print('✓ HSMF import successful')
    except Exception as e:
        print(f'✗ HSMF import failed: {e}')
        return False
    try:
        cm = CertifiedMath()
        print('✓ CertifiedMath instance creation successful')
    except Exception as e:
        print(f'✗ CertifiedMath instance creation failed: {e}')
        return False
    try:
        hsmf = HSMF(cm)
        print('✓ HSMF instance creation successful')
    except Exception as e:
        print(f'✗ HSMF instance creation failed: {e}')
        return False
    required_methods = ['_calculate_I_eff', '_calculate_delta_lambda', '_calculate_delta_h', '_check_atr_coherence', '_check_directional_encoding', '_calculate_action_cost_qfs', '_calculate_c_holo', 'validate_action_bundle']
    for method in sorted(required_methods):
        if hasattr(hsmf, method):
            print(f"✓ Method '{method}' exists")
        else:
            print(f"✗ Method '{method}' missing")
            return False
    required_constants = ['PHI_DEFAULT', 'ONE', 'ZERO', 'ONE_PERCENT']
    for const in sorted(required_constants):
        if hasattr(hsmf, const):
            print(f"✓ Constant '{const}' exists")
        else:
            print(f"✗ Constant '{const}' missing")
            return False
    print('All structural tests passed!')
    return True
if __name__ == '__main__':
    test_hsmf_structure()