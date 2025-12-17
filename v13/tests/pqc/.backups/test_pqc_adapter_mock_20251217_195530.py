"""
TestPQCAdapterMock.py - Layer A Tests for Deterministic PQC Mock Adapter
Tests keygen, sign, verify operations using the deterministic mock adapter with negative tests.

Zero-Simulation Compliant
"""
<<<<<<< HEAD

import sys
import os
=======
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
import json
import hashlib
from typing import Dict, Any
from unittest.mock import patch
<<<<<<< HEAD

# Add the v13 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

=======
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
from v13.libs.adapters.mock_pqc_adapter import MockPQCAdapter
from v13.libs.pqc.CanonicalSerializer import CanonicalSerializer

class TestPQCAdapterMock:
    """
    Test suite for MockPQCAdapter implementing PQCInterface.
    Covers deterministic behavior, tamper detection, and edge cases.
    """

    def __init__(self):
        self.adapter = MockPQCAdapter()
        self.test_results = []
        self.pass_count = 0
        self.fail_count = 0

    def run_all_tests(self):
        """Execute all PQC mock adapter tests."""
<<<<<<< HEAD
        print("=" * 80)
        print("PQC Mock Adapter Tests - Layer A (Deterministic)")
        print("=" * 80)

        # Test 1: Deterministic keygen with fixed seed
        self.test_deterministic_keygen()

        # Test 2: Sign/verify round-trip
        self.test_sign_verify_round_trip()

        # Test 3: Tamper detection
        self.test_tamper_detection()

        # Test 4: Wrong key detection
        self.test_wrong_key_detection()

        # Test 5: Tampered signature detection
        self.test_tampered_signature_detection()

        # Test 6: Edge case - empty message
        self.test_empty_message_handling()

        # Test 7: Edge case - very large message
        self.test_large_message_handling()

        # Print summary
        self.print_summary()

        # Generate evidence artifact
=======
        print('=' * 80)
        print('PQC Mock Adapter Tests - Layer A (Deterministic)')
        print('=' * 80)
        self.test_deterministic_keygen()
        self.test_sign_verify_round_trip()
        self.test_tamper_detection()
        self.test_wrong_key_detection()
        self.test_tampered_signature_detection()
        self.test_empty_message_handling()
        self.test_large_message_handling()
        self.print_summary()
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        self.generate_evidence_artifact()

    def test_deterministic_keygen(self):
        """
        Test: Deterministic keygen with fixed seed produces identical keypairs.
        """
<<<<<<< HEAD
        test_name = "Deterministic Keygen"
        print(f"\n[TEST] {test_name}")

        try:
            # Use a fixed 32-byte seed
            seed = b"mock_test_seed_123456789012345678"  # 32 bytes

            # Generate keypair twice
            priv1, pub1 = self.adapter.keygen(seed)
            priv2, pub2 = self.adapter.keygen(seed)

            # Assert identical results
            if priv1 == priv2 and pub1 == pub2:
                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Deterministic keygen produces identical keypairs",
                    "seed_length": len(seed),
                    "private_key_length": len(priv1),
                    "public_key_length": len(pub1),
                }
=======
        test_name = 'Deterministic Keygen'
        print(f'\n[TEST] {test_name}')
        try:
            seed = b'mock_test_seed_123456789012345678'
            priv1, pub1 = self.adapter.keygen(seed)
            priv2, pub2 = self.adapter.keygen(seed)
            if priv1 == priv2 and pub1 == pub2:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Deterministic keygen produces identical keypairs', 'seed_length': len(seed), 'private_key_length': len(priv1), 'public_key_length': len(pub1)}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
<<<<<<< HEAD
                raise ValueError(
                    "Keygen not deterministic - different results for same seed"
                )

        except Exception as e:
            result = {"test_name": test_name, "status": "FAIL", "error": str(e)}
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")

=======
                raise ValueError('Keygen not deterministic - different results for same seed')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e)}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        self.test_results.append(result)

    def test_sign_verify_round_trip(self):
        """
        Test: Sign/verify round-trip with canonical payload.
        """
<<<<<<< HEAD
        test_name = "Sign/Verify Round-Trip"
        print(f"\n[TEST] {test_name}")

=======
        test_name = 'Sign/Verify Round-Trip'
        print(f'\n[TEST] {test_name}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        try:
            seed = b'sign_roundtrip_seed_123456789012345'
            private_key, public_key = self.adapter.keygen(seed)
<<<<<<< HEAD

            # Create canonical payload
            payload = {
                "module": "TestModule",
                "action": "test_action",
                "data": {"value": 42, "text": "hello world"},
                "timestamp": 1000,
            }
            canonical_bytes = CanonicalSerializer.serialize_data(payload)

            # Sign
            signature = self.adapter.sign(private_key, canonical_bytes)

            # Verify
            is_valid = self.adapter.verify(public_key, canonical_bytes, signature)

            if is_valid:
                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Sign/verify round-trip successful",
                    "payload_hash": hashlib.sha256(canonical_bytes).hexdigest()[:16]
                    + "...",
                    "signature_length": len(signature),
                }
=======
            payload = {'module': 'TestModule', 'action': 'test_action', 'data': {'value': 42, 'text': 'hello world'}, 'timestamp': 1000}
            canonical_bytes = CanonicalSerializer.serialize_data(payload)
            signature = self.adapter.sign(private_key, canonical_bytes)
            is_valid = self.adapter.verify(public_key, canonical_bytes, signature)
            if is_valid:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Sign/verify round-trip successful', 'payload_hash': hashlib.sha256(canonical_bytes).hexdigest()[:16] + '...', 'signature_length': len(signature)}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
<<<<<<< HEAD
                raise ValueError("Signature verification failed")

        except Exception as e:
            result = {"test_name": test_name, "status": "FAIL", "error": str(e)}
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")

=======
                raise ValueError('Signature verification failed')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e)}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        self.test_results.append(result)

    def test_tamper_detection(self):
        """
        Test: Tampered message correctly rejected by verify.
        """
<<<<<<< HEAD
        test_name = "Tamper Detection"
        print(f"\n[TEST] {test_name}")

=======
        test_name = 'Tamper Detection'
        print(f'\n[TEST] {test_name}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        try:
            seed = b'tamper_detect_seed_1234567890123456'
            private_key, public_key = self.adapter.keygen(seed)
<<<<<<< HEAD

            # Create original payload
            original_payload = {
                "module": "TestModule",
                "action": "transfer",
                "amount": "100.0",
                "recipient": "node_123",
            }
            original_bytes = CanonicalSerializer.serialize_data(original_payload)

            # Sign original payload
            signature = self.adapter.sign(private_key, original_bytes)

            # Create tampered payload (change amount)
            tampered_payload = {
                "module": "TestModule",
                "action": "transfer",
                "amount": "999999.0",  # TAMPERED!
                "recipient": "node_123",
            }
            tampered_bytes = CanonicalSerializer.serialize_data(tampered_payload)

            # Verify should fail on tampered payload
            is_valid = self.adapter.verify(public_key, tampered_bytes, signature)

            if not is_valid:
                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Tamper detection working - invalid signature rejected",
                    "original_hash": hashlib.sha256(original_bytes).hexdigest()[:16]
                    + "...",
                    "tampered_hash": hashlib.sha256(tampered_bytes).hexdigest()[:16]
                    + "...",
                }
=======
            original_payload = {'module': 'TestModule', 'action': 'transfer', 'amount': '100.0', 'recipient': 'node_123'}
            original_bytes = CanonicalSerializer.serialize_data(original_payload)
            signature = self.adapter.sign(private_key, original_bytes)
            tampered_payload = {'module': 'TestModule', 'action': 'transfer', 'amount': '999999.0', 'recipient': 'node_123'}
            tampered_bytes = CanonicalSerializer.serialize_data(tampered_payload)
            is_valid = self.adapter.verify(public_key, tampered_bytes, signature)
            if not is_valid:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Tamper detection working - invalid signature rejected', 'original_hash': hashlib.sha256(original_bytes).hexdigest()[:16] + '...', 'tampered_hash': hashlib.sha256(tampered_bytes).hexdigest()[:16] + '...'}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
<<<<<<< HEAD
                raise ValueError(
                    "Tamper detection failed - signature accepted for tampered data"
                )

        except Exception as e:
            result = {"test_name": test_name, "status": "FAIL", "error": str(e)}
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")

=======
                raise ValueError('Tamper detection failed - signature accepted for tampered data')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e)}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        self.test_results.append(result)

    def test_wrong_key_detection(self):
        """
        Test: Verification fails with wrong public key.
        """
<<<<<<< HEAD
        test_name = "Wrong Key Detection"
        print(f"\n[TEST] {test_name}")

=======
        test_name = 'Wrong Key Detection'
        print(f'\n[TEST] {test_name}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        try:
            seed1 = b'wrong_key_seed_1_12345678901234567'
            seed2 = b'wrong_key_seed_2_12345678901234567'
            private_key1, public_key1 = self.adapter.keygen(seed1)
            private_key2, public_key2 = self.adapter.keygen(seed2)
<<<<<<< HEAD

            # Create payload
            payload = {"test": "data"}
            canonical_bytes = CanonicalSerializer.serialize_data(payload)

            # Sign with first key
            signature = self.adapter.sign(private_key1, canonical_bytes)

            # Verify with second key (should fail)
            is_valid = self.adapter.verify(public_key2, canonical_bytes, signature)

            if not is_valid:
                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Wrong key detection working - verification failed with wrong key",
                }
=======
            payload = {'test': 'data'}
            canonical_bytes = CanonicalSerializer.serialize_data(payload)
            signature = self.adapter.sign(private_key1, canonical_bytes)
            is_valid = self.adapter.verify(public_key2, canonical_bytes, signature)
            if not is_valid:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Wrong key detection working - verification failed with wrong key'}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
<<<<<<< HEAD
                raise ValueError(
                    "Wrong key detection failed - signature accepted with wrong key"
                )

        except Exception as e:
            result = {"test_name": test_name, "status": "FAIL", "error": str(e)}
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")

=======
                raise ValueError('Wrong key detection failed - signature accepted with wrong key')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e)}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        self.test_results.append(result)

    def test_tampered_signature_detection(self):
        """
        Test: Verification fails with tampered signature.
        """
<<<<<<< HEAD
        test_name = "Tampered Signature Detection"
        print(f"\n[TEST] {test_name}")

=======
        test_name = 'Tampered Signature Detection'
        print(f'\n[TEST] {test_name}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        try:
            seed = b'tamper_sig_seed_123456789012345678'
            private_key, public_key = self.adapter.keygen(seed)
<<<<<<< HEAD

            # Create payload
            payload = {"test": "data"}
            canonical_bytes = CanonicalSerializer.serialize_data(payload)

            # Sign
            signature = self.adapter.sign(private_key, canonical_bytes)

            # Tamper with signature (flip some bits)
=======
            payload = {'test': 'data'}
            canonical_bytes = CanonicalSerializer.serialize_data(payload)
            signature = self.adapter.sign(private_key, canonical_bytes)
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
            tampered_signature = bytearray(signature)
            tampered_signature[0] ^= 255
            tampered_signature = bytes(tampered_signature)
<<<<<<< HEAD

            # Verify should fail
            is_valid = self.adapter.verify(
                public_key, canonical_bytes, tampered_signature
            )

            if not is_valid:
                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Tampered signature detection working - verification failed",
                }
=======
            is_valid = self.adapter.verify(public_key, canonical_bytes, tampered_signature)
            if not is_valid:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Tampered signature detection working - verification failed'}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
<<<<<<< HEAD
                raise ValueError(
                    "Tampered signature detection failed - tampered signature accepted"
                )

        except Exception as e:
            result = {"test_name": test_name, "status": "FAIL", "error": str(e)}
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")

=======
                raise ValueError('Tampered signature detection failed - tampered signature accepted')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e)}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        self.test_results.append(result)

    def test_empty_message_handling(self):
        """
        Test: Handle empty message correctly.
        """
<<<<<<< HEAD
        test_name = "Empty Message Handling"
        print(f"\n[TEST] {test_name}")

=======
        test_name = 'Empty Message Handling'
        print(f'\n[TEST] {test_name}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        try:
            seed = b'empty_msg_seed_1234567890123456789'
            private_key, public_key = self.adapter.keygen(seed)
<<<<<<< HEAD

            # Empty message
            empty_message = b""

            # Sign empty message
            signature = self.adapter.sign(private_key, empty_message)

            # Verify
            is_valid = self.adapter.verify(public_key, empty_message, signature)

            if is_valid:
                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Empty message handling successful",
                }
=======
            empty_message = b''
            signature = self.adapter.sign(private_key, empty_message)
            is_valid = self.adapter.verify(public_key, empty_message, signature)
            if is_valid:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Empty message handling successful'}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
<<<<<<< HEAD
                raise ValueError("Empty message verification failed")

        except Exception as e:
            result = {"test_name": test_name, "status": "FAIL", "error": str(e)}
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")

=======
                raise ValueError('Empty message verification failed')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e)}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        self.test_results.append(result)

    def test_large_message_handling(self):
        """
        Test: Handle large message correctly.
        """
<<<<<<< HEAD
        test_name = "Large Message Handling"
        print(f"\n[TEST] {test_name}")

=======
        test_name = 'Large Message Handling'
        print(f'\n[TEST] {test_name}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        try:
            seed = b'large_msg_seed_123456789012345678'
            private_key, public_key = self.adapter.keygen(seed)
<<<<<<< HEAD

            # Large message (1MB of data)
            large_message = b"A" * (1024 * 1024)  # 1MB

            # Sign large message
            signature = self.adapter.sign(private_key, large_message)

            # Verify
            is_valid = self.adapter.verify(public_key, large_message, signature)

            if is_valid:
                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Large message handling successful",
                    "message_size_bytes": len(large_message),
                }
=======
            large_message = b'A' * (1024 * 1024)
            signature = self.adapter.sign(private_key, large_message)
            is_valid = self.adapter.verify(public_key, large_message, signature)
            if is_valid:
                result = {'test_name': test_name, 'status': 'PASS', 'description': 'Large message handling successful', 'message_size_bytes': len(large_message)}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
                self.pass_count += 1
                print(f'  ✅ PASS: {test_name}')
            else:
<<<<<<< HEAD
                raise ValueError("Large message verification failed")

        except Exception as e:
            result = {"test_name": test_name, "status": "FAIL", "error": str(e)}
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")

=======
                raise ValueError('Large message verification failed')
        except Exception as e:
            result = {'test_name': test_name, 'status': 'FAIL', 'error': str(e)}
            self.fail_count += 1
            print(f'  ❌ FAIL: {test_name} - {e}')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        self.test_results.append(result)

    def print_summary(self):
        """Print test summary."""
        total_tests = self.pass_count + self.fail_count
<<<<<<< HEAD
        pass_rate = (self.pass_count / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "=" * 80)
        print("PQC MOCK ADAPTER TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests:  {total_tests}")
        print(f"Passed:       {self.pass_count} ✅")
        print(f"Failed:       {self.fail_count} ❌")
        print(f"Pass Rate:    {pass_rate:.1f}%")
        print("=" * 80)
=======
        pass_rate = self.pass_count / total_tests * 100 if total_tests > 0 else 0
        print('\n' + '=' * 80)
        print('PQC MOCK ADAPTER TEST SUMMARY')
        print('=' * 80)
        print(f'Total Tests:  {total_tests}')
        print(f'Passed:       {self.pass_count} ✅')
        print(f'Failed:       {self.fail_count} ❌')
        print(f'Pass Rate:    {pass_rate:.1f}%')
        print('=' * 80)
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)

    def generate_evidence_artifact(self):
        """Generate evidence artifact for audit trail."""
        import json
<<<<<<< HEAD
        from datetime import datetime, timezone

        evidence_dir = os.path.join(os.path.dirname(__file__), "../../evidence/v13_6")
        os.makedirs(evidence_dir, exist_ok=True)

        evidence_path = os.path.join(evidence_dir, "pqc_mock_verification.json")

        evidence = {
            "artifact_type": "pqc_mock_verification",
            "version": "V13.6",
            "test_suite": "test_pqc_adapter_mock.py",
            "layer": "A - Deterministic Mock",
            "timestamp": "2024-01-01T00:00:00.000000Z",
            "summary": {
                "total_tests": self.pass_count + self.fail_count,
                "passed": self.pass_count,
                "failed": self.fail_count,
                "pass_rate_percent": (
                    self.pass_count / (self.pass_count + self.fail_count) * 100
                )
                if (self.pass_count + self.fail_count) > 0
                else 0,
            },
            "test_results": self.test_results,
            "backend_info": {
                "backend": "MockPQCAdapter",
                "algorithm": "SHA-256 (simulation only)",
                "security_level": "NONE - NOT CRYPTOGRAPHICALLY SECURE",
                "production_ready": False,
                "quantum_resistant": False,
                "deterministic": True,
                "warning": "INTEGRATION TESTING ONLY - DO NOT USE IN PRODUCTION",
            },
        }

        with open(evidence_path, "w") as f:
            json.dump(evidence, f, indent=2)

        print(f"\n📄 Evidence artifact generated: {evidence_path}")


if __name__ == "__main__":
    print("QFS V13.6 - PQC Mock Adapter Verification (Layer A)")
    print("Testing deterministic keygen, sign/verify, and tamper detection")
    print()

    tester = TestPQCAdapterMock()
    tester.run_all_tests()

    print("\n✅ PQC mock adapter verification complete!")
    print("Evidence artifact: evidence/v13_6/pqc_mock_verification.json")
=======
        evidence_dir = os.path.join(os.path.dirname(__file__), '../../evidence/v13_6')
        os.makedirs(evidence_dir, exist_ok=True)
        evidence_path = os.path.join(evidence_dir, 'pqc_mock_verification.json')
        evidence = {'artifact_type': 'pqc_mock_verification', 'version': 'V13.6', 'test_suite': 'test_pqc_adapter_mock.py', 'layer': 'A - Deterministic Mock', 'timestamp': datetime.now(timezone.utc).isoformat() + 'Z', 'summary': {'total_tests': self.pass_count + self.fail_count, 'passed': self.pass_count, 'failed': self.fail_count, 'pass_rate_percent': self.pass_count / (self.pass_count + self.fail_count) * 100 if self.pass_count + self.fail_count > 0 else 0}, 'test_results': self.test_results, 'backend_info': {'backend': 'MockPQCAdapter', 'algorithm': 'SHA-256 (simulation only)', 'security_level': 'NONE - NOT CRYPTOGRAPHICALLY SECURE', 'production_ready': False, 'quantum_resistant': False, 'deterministic': True, 'warning': 'INTEGRATION TESTING ONLY - DO NOT USE IN PRODUCTION'}}
        with open(evidence_path, 'w') as f:
            json.dump(evidence, f, indent=2)
        print(f'\n📄 Evidence artifact generated: {evidence_path}')
if __name__ == '__main__':
    print('QFS V13.6 - PQC Mock Adapter Verification (Layer A)')
    print('Testing deterministic keygen, sign/verify, and tamper detection')
    print()
    tester = TestPQCAdapterMock()
    tester.run_all_tests()
    print('\n✅ PQC mock adapter verification complete!')
    print('Evidence artifact: evidence/v13_6/pqc_mock_verification.json')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
