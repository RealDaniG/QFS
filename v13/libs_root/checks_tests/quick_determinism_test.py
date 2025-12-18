"""
Quick Determinism Test for QFS V13
Simple test to verify deterministic behavior of core components
"""
import json
import hashlib
from CertifiedMath import BigNum128, CertifiedMath
from PQC import PQC
from HSMF import HSMF, ValidationResult
from DRV_Packet import DRV_Packet
from TokenStateBundle import TokenStateBundle, create_token_state_bundle
from CIR302_Handler import CIR302_Handler, QuarantineResult

def deterministic_hash(data):
    """Generate deterministic SHA-256 hash of data."""
    if isinstance(data, str):
        serialized = data
    else:
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

def test_determinism():
    """Test deterministic behavior of all components."""
    print('Testing QFS V13 Deterministic Behavior')
    print('=' * 40)
    print('1. CertifiedMath deterministic operations...')
    with CertifiedMath.LogContext() as log1:
        a = BigNum128.from_int(2)
        b = BigNum128.from_int(3)
        result = CertifiedMath.add(a, b, log1)
        result1 = result.to_decimal_string()
    with CertifiedMath.LogContext() as log2:
        a = BigNum128.from_int(2)
        b = BigNum128.from_int(3)
        result = CertifiedMath.add(a, b, log2)
        result2 = result.to_decimal_string()
    assert result1 == result2, 'CertifiedMath not deterministic'
    print(f'   ✅ 2 + 3 = {result1}')
    print('2. PQC deterministic operations...')
    seed = b'test_seed_123'
    with PQC.LogContext() as log1:
        keypair1 = PQC.generate_keypair(log_list=log1, seed=seed)
        pubkey1 = keypair1.public_key.hex()
    with PQC.LogContext() as log2:
        keypair2 = PQC.generate_keypair(log_list=log2, seed=seed)
        pubkey2 = keypair2.public_key.hex()
    assert pubkey1 == pubkey2, 'PQC key generation not deterministic'
    print(f'   ✅ Key generation deterministic')
    print('3. DRV_Packet deterministic operations...')
    packet1 = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed', metadata={'test': 'data'})
    hash1 = packet1.get_hash()
    packet2 = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed', metadata={'test': 'data'})
    hash2 = packet2.get_hash()
    assert hash1 == hash2, 'DRV_Packet not deterministic'
    print(f'   ✅ Packet creation deterministic')
    print('4. TokenStateBundle deterministic operations...')
    bundle1 = create_token_state_bundle(chr_state={'coherence_metric': '0.95'}, flx_state={'scaling_metric': '0.15'}, psi_sync_state={'frequency_metric': '0.08'}, atr_state={'directional_metric': '0.85'}, res_state={'inertial_metric': '0.05'}, lambda1=BigNum128.from_int(2), lambda2=BigNum128.from_int(3), c_crit=BigNum128.from_int(1), pqc_cid='test_001', timestamp=1700000000)
    bundle_hash1 = bundle1.get_deterministic_hash()
    bundle2 = create_token_state_bundle(chr_state={'coherence_metric': '0.95'}, flx_state={'scaling_metric': '0.15'}, psi_sync_state={'frequency_metric': '0.08'}, atr_state={'directional_metric': '0.85'}, res_state={'inertial_metric': '0.05'}, lambda1=BigNum128.from_int(2), lambda2=BigNum128.from_int(3), c_crit=BigNum128.from_int(1), pqc_cid='test_001', timestamp=1700000000)
    bundle_hash2 = bundle2.get_deterministic_hash()
    assert bundle_hash1 == bundle_hash2, 'TokenStateBundle not deterministic'
    print(f'   ✅ Bundle creation deterministic')
    test_data = {'certifiedmath': result1, 'pqc_pubkey': pubkey1[:32] + '...', 'drv_packet_hash': hash1[:32] + '...', 'bundle_hash': bundle_hash1[:32] + '...'}
    test_hash = deterministic_hash(test_data)
    print(f'\nOverall test hash: {test_hash}')
    print('✅ All components demonstrate deterministic behavior!')
if __name__ == '__main__':
    test_determinism()
