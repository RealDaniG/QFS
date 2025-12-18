"""
TestPQCAdapters.py - Tests for PQC Adapter Implementations
Verifies deterministic keygen, sign/verify round-trips, and message integration
"""
import json
import hashlib
from typing import Dict, Any
from v13.libs.cee.adapters.pqc_adapter_factory import PQCAdapterFactory
from v13.libs.cee.interfaces.message_protocol import SignedMessage
from v13.libs.pqc.CanonicalSerializer import CanonicalSerializer

class TestPQCAdapters:
    """
    Test suite for PQC adapters implementing PQCInterfaceProtocol.
    """

    def __init__(self):
        self.adapter, self.backend_name = PQCAdapterFactory.create_adapter()
        self.test_results = []
        self.pass_count = 0
        self.fail_count = 0

    def run_all_tests(self):
        """Execute all PQC adapter tests."""
        print('=' * 80)
        print(f'PQC Adapter Tests - Backend: {self.backend_name}')
        print('=' * 80)
        self.test_deterministic_keygen()
        self.test_sign_verify_round_trip()
        self.test_tamper_detection()
        self.test_signed_message_integration()
        self.print_summary()
        self.generate_evidence_artifact()

    def test_deterministic_keygen(self):
        """
        Test: Deterministic keygen with fixed seed produces identical keypairs.
        """
        test_name = 'Deterministic Keygen'
        print(f'\n[TEST] {test_name}')
        try:
            seed = b'test_seed_1234567890123456789012'
            priv1, pub1 = self.adapter.keygen(seed)
            priv2, pub2 = self.adapter.keygen(seed)
            if priv1 == priv2 and pub1 == pub2:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Deterministic keygen produces identical keypairs', 'seed_length': len(seed), 'private_key_length': len(priv1), 'public_key_length': len(pub1), 'backend': self.backend_name}
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
                raise ValueError('Keygen not deterministic - different results for same seed')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e), 'backend': self.backend_name}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
        self.test_results.append(result)

    def test_sign_verify_round_trip(self):
        """
        Test: Sign/verify round-trip with canonical payload.
        """
        test_name = 'Sign/Verify Round-Trip'
        print(f'\n[TEST] {test_name}')
        try:
            seed = b'sign_test_seed_12345678901234567'
            private_key, public_key = self.adapter.keygen(seed)
            payload = {'module': 'TestModule', 'action': 'test_action', 'data': {'value': 42, 'text': 'hello world'}, 'timestamp': 1000}
            canonical_bytes = CanonicalSerializer.serialize_data(payload)
            signature = self.adapter.sign(private_key, canonical_bytes)
            is_valid = self.adapter.verify(public_key, canonical_bytes, signature)
            if is_valid:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Sign/verify round-trip successful', 'payload_hash': hashlib.sha256(canonical_bytes).hexdigest(), 'signature_length': len(signature), 'backend': self.backend_name}
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
                raise ValueError('Signature verification failed')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e), 'backend': self.backend_name}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
        self.test_results.append(result)

    def test_tamper_detection(self):
        """
        Test: Tampered message correctly rejected by verify.
        """
        test_name = 'Tamper Detection'
        print(f'\n[TEST] {test_name}')
        try:
            seed = b'tamper_test_seed_1234567890123456'
            private_key, public_key = self.adapter.keygen(seed)
            original_payload = {'module': 'TestModule', 'action': 'transfer', 'amount': '100.0', 'recipient': 'node_123'}
            original_bytes = CanonicalSerializer.serialize_data(original_payload)
            signature = self.adapter.sign(private_key, original_bytes)
            tampered_payload = {'module': 'TestModule', 'action': 'transfer', 'amount': '999999.0', 'recipient': 'node_123'}
            tampered_bytes = CanonicalSerializer.serialize_data(tampered_payload)
            is_valid = self.adapter.verify(public_key, tampered_bytes, signature)
            if not is_valid:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Tamper detection working - invalid signature rejected', 'original_hash': hashlib.sha256(original_bytes).hexdigest(), 'tampered_hash': hashlib.sha256(tampered_bytes).hexdigest(), 'backend': self.backend_name}
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
                raise ValueError('Tamper detection failed - signature accepted for tampered data')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e), 'backend': self.backend_name}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
        self.test_results.append(result)

    def test_signed_message_integration(self):
        """
        Test: SignedMessage creation and verification using PQC adapter.
        """
        test_name = 'SignedMessage Integration'
        print(f'\n[TEST] {test_name}')
        try:
            seed = b'message_test_seed_123456789012345'
            private_key, public_key = self.adapter.keygen(seed)
            payload = {'reward_type': 'CHR', 'amount': '50.0', 'recipient': 'user_abc123', 'reason': 'coherence_contribution'}
            message = SignedMessage.create(sender_qid='test_node_001', recipient_module='RewardAllocator', payload=payload, tick=100, timestamp=1000, private_key=private_key, public_key=public_key, pqc=self.adapter)
            is_valid = message.verify(self.adapter)
            if is_valid:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'SignedMessage creation and verification successful', 'sender': message.sender_qid, 'recipient': message.recipient_module, 'tick': message.tick, 'backend': self.backend_name}
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
                raise ValueError('SignedMessage verification failed')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e), 'backend': self.backend_name}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
        self.test_results.append(result)

    def print_summary(self):
        """Print test summary."""
        total_tests = self.pass_count + self.fail_count
        pass_rate = self.pass_count / total_tests * 100 if total_tests > 0 else 0
        print('\n' + '=' * 80)
        print('PQC ADAPTER TEST SUMMARY')
        print('=' * 80)
        print(f'Backend:      {self.backend_name}')
        print(f'Total Tests:  {total_tests}')
        print(f'Passed:       {self.pass_count} ✅')
        print(f'Failed:       {self.fail_count} ❌')
        print(f'Pass Rate:    {pass_rate:.1f}%')
        print('=' * 80)

    def generate_evidence_artifact(self):
        """Generate evidence artifact for audit trail."""
        import json
        evidence_dir = os.path.join(os.path.dirname(__file__), '../../evidence/v13_6')
        os.makedirs(evidence_dir, exist_ok=True)
        evidence_path = os.path.join(evidence_dir, 'pqc_adapter_verification.json')
        evidence = {'artifact_type': 'pqc_adapter_verification', 'version': 'V13.6', 'test_suite': 'TestPQCAdapters.py', 'backend': self.backend_name, 'backend_info': PQCAdapterFactory.get_backend_info(), 'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z', 'summary': {'total_tests': self.pass_count + self.fail_count, 'passed': self.pass_count, 'failed': self.fail_count, 'pass_rate_percent': self.pass_count / (self.pass_count + self.fail_count) * 100 if self.pass_count + self.fail_count > 0 else 0}, 'test_results': self.test_results}
        with open(evidence_path, 'w') as f:
            json.dump(evidence, f, indent=2)
        print(f'\n📄 Evidence artifact generated: {evidence_path}')
if __name__ == '__main__':
    print('QFS V13.6 - PQC Adapter Verification')
    print('Testing deterministic keygen, sign/verify, and message integration')
    print()
    tester = TestPQCAdapters()
    tester.run_all_tests()
    print('\n✅ PQC adapter verification complete!')
    print('Evidence artifact: evidence/v13_6/pqc_adapter_verification.json')
