"""
TestPQCRealBackend.py - Layer B Tests for Real PQC Backend
Tests PQC operations using the real backend (liboqs or pqcrystals) when available.

Zero-Simulation Compliant
"""
import sys
import os
import json
import hashlib
from typing import Dict, Any

# Add the v13 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from v13.libs.adapters.pqc_adapter_factory import PQCAdapterFactory
from v13.libs.pqc.CanonicalSerializer import CanonicalSerializer
from v13.libs.pqc.PQC_Core import PQC


class TestPQCRealBackend:
    """
    Test suite for real PQC backend (liboqs or pqcrystals).
    Only runs when QFS_REAL_PQC_AVAILABLE environment variable is set to 1.
    """
    
    def __init__(self):
        self.adapter, self.backend_name = PQCAdapterFactory.create_adapter()
        self.test_results = []
        self.pass_count = 0
        self.fail_count = 0
    
    def run_all_tests(self):
        """Execute all PQC real backend tests."""
        print("=" * 80)
        print(f"PQC Real Backend Tests - Layer B ({self.backend_name})")
        print("=" * 80)
        
        # Test 1: Deterministic keygen with proper seed length
        self.test_deterministic_keygen()
        
        # Test 2: Sign/verify round-trip
        self.test_sign_verify_round_trip()
        
        # Test 3: Tamper detection
        self.test_tamper_detection()
        
        # Test 4: Wrong key detection
        self.test_wrong_key_detection()
        
        # Test 5: Large message handling
        self.test_large_message_handling()
        
        # Print summary
        self.print_summary()
        
        # Generate evidence artifact
        self.generate_evidence_artifact()
    
    def test_deterministic_keygen(self):
        """
        Test: Deterministic keygen with 32-byte seed produces identical keypairs.
        """
        test_name = "Deterministic Keygen"
        print(f"\n[TEST] {test_name}")
        
        try:
            # Use a fixed 32-byte seed as required for Dilithium5
            seed = b"real_test_seed_1234567890123456789"  # 32 bytes
            
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
                    "backend": self.backend_name
                }
                self.pass_count += 1
                print(f"  ✅ PASS: {test_name}")
            else:
                raise ValueError("Keygen not deterministic - different results for same seed")
                
        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "backend": self.backend_name
            }
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")
        
        self.test_results.append(result)
    
    def test_sign_verify_round_trip(self):
        """
        Test: Sign/verify round-trip with canonical payload.
        """
        test_name = "Sign/Verify Round-Trip"
        print(f"\n[TEST] {test_name}")
        
        try:
            # Generate keys
            seed = b"sign_roundtrip_seed_1234567890123456"  # 32 bytes
            private_key, public_key = self.adapter.keygen(seed)
            
            # Create canonical payload
            payload = {
                "module": "TestModule",
                "action": "test_action",
                "data": {"value": 42, "text": "hello world"},
                "timestamp": 1000
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
                    "payload_hash": hashlib.sha256(canonical_bytes).hexdigest()[:16] + "...",
                    "signature_length": len(signature),
                    "backend": self.backend_name
                }
                self.pass_count += 1
                print(f"  ✅ PASS: {test_name}")
            else:
                raise ValueError("Signature verification failed")
                
        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "backend": self.backend_name
            }
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")
        
        self.test_results.append(result)
    
    def test_tamper_detection(self):
        """
        Test: Tampered message correctly rejected by verify.
        """
        test_name = "Tamper Detection"
        print(f"\n[TEST] {test_name}")
        
        try:
            # Generate keys
            seed = b"tamper_detect_seed_12345678901234567"  # 32 bytes
            private_key, public_key = self.adapter.keygen(seed)
            
            # Create original payload
            original_payload = {
                "module": "TestModule",
                "action": "transfer",
                "amount": "100.0",
                "recipient": "node_123"
            }
            original_bytes = CanonicalSerializer.serialize_data(original_payload)
            
            # Sign original payload
            signature = self.adapter.sign(private_key, original_bytes)
            
            # Create tampered payload (change amount)
            tampered_payload = {
                "module": "TestModule",
                "action": "transfer",
                "amount": "999999.0",  # TAMPERED!
                "recipient": "node_123"
            }
            tampered_bytes = CanonicalSerializer.serialize_data(tampered_payload)
            
            # Verify should fail on tampered payload
            is_valid = self.adapter.verify(public_key, tampered_bytes, signature)
            
            if not is_valid:
                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Tamper detection working - invalid signature rejected",
                    "original_hash": hashlib.sha256(original_bytes).hexdigest()[:16] + "...",
                    "tampered_hash": hashlib.sha256(tampered_bytes).hexdigest()[:16] + "...",
                    "backend": self.backend_name
                }
                self.pass_count += 1
                print(f"  ✅ PASS: {test_name}")
            else:
                raise ValueError("Tamper detection failed - signature accepted for tampered data")
                
        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "backend": self.backend_name
            }
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")
        
        self.test_results.append(result)
    
    def test_wrong_key_detection(self):
        """
        Test: Verification fails with wrong public key.
        """
        test_name = "Wrong Key Detection"
        print(f"\n[TEST] {test_name}")
        
        try:
            # Generate two different keypairs
            seed1 = b"wrong_key_seed_1_123456789012345678"  # 32 bytes
            seed2 = b"wrong_key_seed_2_123456789012345678"  # 32 bytes
            private_key1, public_key1 = self.adapter.keygen(seed1)
            private_key2, public_key2 = self.adapter.keygen(seed2)
            
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
                    "backend": self.backend_name
                }
                self.pass_count += 1
                print(f"  ✅ PASS: {test_name}")
            else:
                raise ValueError("Wrong key detection failed - signature accepted with wrong key")
                
        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "backend": self.backend_name
            }
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")
        
        self.test_results.append(result)
    
    def test_large_message_handling(self):
        """
        Test: Handle large message correctly.
        """
        test_name = "Large Message Handling"
        print(f"\n[TEST] {test_name}")
        
        try:
            # Generate keypair
            seed = b"large_msg_seed_1234567890123456789"  # 32 bytes
            private_key, public_key = self.adapter.keygen(seed)
            
            # Large message (100KB of data)
            large_message = b"A" * (100 * 1024)  # 100KB
            
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
                    "signature_length": len(signature),
                    "backend": self.backend_name
                }
                self.pass_count += 1
                print(f"  ✅ PASS: {test_name}")
            else:
                raise ValueError("Large message verification failed")
                
        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "backend": self.backend_name
            }
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {e}")
        
        self.test_results.append(result)
    
    def print_summary(self):
        """Print test summary."""
        total_tests = self.pass_count + self.fail_count
        pass_rate = (self.pass_count / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("PQC REAL BACKEND TEST SUMMARY")
        print("=" * 80)
        print(f"Backend:      {self.backend_name}")
        print(f"Total Tests:  {total_tests}")
        print(f"Passed:       {self.pass_count} ✅")
        print(f"Failed:       {self.fail_count} ❌")
        print(f"Pass Rate:    {pass_rate:.1f}%")
        print("=" * 80)
    
    def generate_evidence_artifact(self):
        """Generate evidence artifact for audit trail."""
        import os
        import json
        from datetime import datetime, timezone
        
        evidence_dir = os.path.join(os.path.dirname(__file__), '../../docs/evidence/v13_6')
        os.makedirs(evidence_dir, exist_ok=True)
        
        evidence_path = os.path.join(evidence_dir, 'pqc_real_backend_verification.json')
        
        # Get backend info
        backend_info = PQCAdapterFactory.get_backend_info()
        
        evidence = {
            "artifact_type": "pqc_real_backend_verification",
            "version": "V13.6",
            "test_suite": "test_pqc_real_backend.py",
            "layer": "B - Real Backend",
            "backend": self.backend_name,
            "backend_info": backend_info,
            "environment": {
                "QFS_REAL_PQC_AVAILABLE": os.environ.get("QFS_REAL_PQC_AVAILABLE", "0"),
                "platform": sys.platform,
                "python_version": sys.version
            },
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "summary": {
                "total_tests": self.pass_count + self.fail_count,
                "passed": self.pass_count,
                "failed": self.fail_count,
                "pass_rate_percent": (self.pass_count / (self.pass_count + self.fail_count) * 100) if (self.pass_count + self.fail_count) > 0 else 0
            },
            "test_results": self.test_results
        }
        
        with open(evidence_path, 'w') as f:
            json.dump(evidence, f, indent=2)
        
        print(f"\n📄 Evidence artifact generated: {evidence_path}")


def main():
    """Main entry point - only run if real PQC is available."""
    # Check if real PQC backend is available
    if os.environ.get("QFS_REAL_PQC_AVAILABLE") != "1":
        print("Skipping PQC real backend tests - QFS_REAL_PQC_AVAILABLE not set to 1")
        print("To run these tests, set environment variable QFS_REAL_PQC_AVAILABLE=1")
        return
    
    # Get backend info to check if we have a real backend
    backend_info = PQCAdapterFactory.get_backend_info()
    if not backend_info.get("production_ready", False):
        print(f"Skipping PQC real backend tests - backend is not production ready: {backend_info.get('backend')}")
        print("These tests require a real PQC backend (liboqs or pqcrystals)")
        return
    
    print("QFS V13.6 - PQC Real Backend Verification (Layer B)")
    print("Testing real PQC backend operations")
    print()
    
    tester = TestPQCRealBackend()
    tester.run_all_tests()
    
    print("\n✅ PQC real backend verification complete!")
    print("Evidence artifact: docs/evidence/v13_6/pqc_real_backend_verification.json")


if __name__ == "__main__":
    main()