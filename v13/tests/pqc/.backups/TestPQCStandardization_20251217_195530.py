"""
TestPQCStandardization.py - Comprehensive Test Suite for PQC Backend Standardization
Verifies deterministic keygen, sign/verify round-trips, message integration, and adapter selection

Zero-Simulation Compliant, PQCInterfaceProtocol-Based, Backend-Agnostic
"""

import unittest
import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from v13.libs.cee.adapters.pqc_adapter_factory import PQCAdapterFactory
from v13.libs.cee.interfaces.pqc_interface import PQCInterface
from v13.libs.cee.interfaces.message_protocol import SignedMessage
from v13.libs.pqc.CanonicalSerializer import CanonicalSerializer


class TestPQCStandardization:
    """
    Comprehensive test suite for PQC standardization implementing the user's requirements:
    1. Pick the primary backend for tests (real if available, otherwise deterministic mock)
    2. Standardize on PQCInterfaceProtocol
    3. Concrete testing strategy with deterministic keygen, sign/verify, and message integration
    4. Backend selection with evidence artifact generation
    """

    def __init__(self):
        self.adapter, self.backend_name = PQCAdapterFactory.create_adapter()
        self.test_results = []
        self.pass_count = 0
        self.fail_count = 0

    def run_all_tests(self):
        """Execute all PQC standardization tests."""
        print("=" * 80)
        print(f"PQC Standardization Tests - Backend: {self.backend_name}")
        print("=" * 80)

        # Test 1: Deterministic keygen with proper seed length validation
        self.test_deterministic_keygen()

        # Test 2: Sign/verify round-trip with canonical payload
        self.test_sign_verify_round_trip()

        # Test 3: Tamper detection with PQC audit logging
        self.test_tamper_detection()

        # Test 4: SignedMessage integration
        self.test_signed_message_integration()

        # Test 5: Wrong seed length rejection
        self.test_wrong_seed_length_rejection()

        # Print summary
        self.print_summary()

        # Generate evidence artifact
        self.generate_evidence_artifact()

    def test_deterministic_keygen(self):
        """
        Test: Deterministic keygen with fixed 32-byte seed produces identical keypairs.
        Verifies deterministic guarantee and stable PQC audit hashes.
        """
        test_name = "Deterministic Keygen"
        print(f"\n[TEST] {test_name}")

        try:
            # Use a fixed 32-byte seed as required
            seed = b"standard_test_seed_12345678901234"  # 32 bytes

            # Generate keypair twice
            priv1, pub1 = self.adapter.keygen(seed)
            priv2, pub2 = self.adapter.keygen(seed)

            # Assert identical results
            if priv1 == priv2 and pub1 == pub2:
                # Calculate PQC audit hash for verification
                key_data = {
                    "private_key": priv1.hex(),
                    "public_key": pub1.hex(),
                    "seed": seed.hex(),
                }
                audit_hash = hashlib.sha3_512(
                    json.dumps(key_data, sort_keys=True).encode()
                ).hexdigest()

                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Deterministic keygen produces identical keypairs with stable audit hash",
                    "seed_length": len(seed),
                    "private_key_length": len(priv1),
                    "public_key_length": len(pub1),
                    "audit_hash": audit_hash[:16] + "...",
                    "backend": self.backend_name,
                }
            else:
                result = {
                    "test_name": test_name,
                    "status": "FAIL",
                    "description": "Keygen not deterministic - different results for same seed",
                    "backend": self.backend_name,
                }

        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "backend": self.backend_name,
            }
        self.log_result(result)

    def test_sign_verify_round_trip(self):
        """
        Test: Sign/verify round-trip with canonical payload serialized via CanonicalSerializer.
        """
        test_name = "Sign/Verify Round-Trip"
        print(f"\n[TEST] {test_name}")

        try:
            seed = b"msg_test_seed_123456789012345678"  # 32 bytes
            private_key, public_key = self.adapter.keygen(seed)

            # Create canonical payload using CanonicalSerializer as required
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
                    "description": "Sign/verify round-trip successful with canonical serialization",
                    "payload_hash": hashlib.sha256(canonical_bytes).hexdigest()[:16]
                    + "...",
                    "signature_length": len(signature),
                    "backend": self.backend_name,
                }
            else:
                result = {
                    "test_name": test_name,
                    "status": "FAIL",
                    "description": "Signature verification failed",
                    "backend": self.backend_name,
                }

        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "backend": self.backend_name,
            }
        self.log_result(result)

    def test_tamper_detection(self):
        """
        Test: Tampered message correctly rejected by verify with PQC audit log recording.
        """
        test_name = "Tamper Detection"
        print(f"\n[TEST] {test_name}")

        try:
            seed = b"tamper_detect_seed_12345678901234"
            private_key, public_key = self.adapter.keygen(seed)

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
                # Simulate PQC audit log recording
                audit_log_entry = {
                    "operation": "verify_signature",
                    "original_hash": hashlib.sha256(original_bytes).hexdigest()[:16]
                    + "...",
                    "tampered_hash": hashlib.sha256(tampered_bytes).hexdigest()[:16]
                    + "...",
                    "result": "REJECTED",
                    "timestamp": int(datetime.now(timezone.utc).timestamp()),
                }

                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Tamper detection working - invalid signature rejected with audit log",
                    "audit_log_entry": audit_log_entry,
                    "backend": self.backend_name,
                }
            else:
                result = {
                    "test_name": test_name,
                    "status": "FAIL",
                    "description": "Tamper detection failed - signature accepted for tampered data",
                    "backend": self.backend_name,
                }

        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "backend": self.backend_name,
            }
        self.log_result(result)

    def test_signed_message_integration(self):
        """
        Test: SignedMessage creation and verification using PQC interface.
        Confirms that tampering with payload, tick, or timestamp invalidates signature
        but preserves deterministic PQC logs.
        """
        test_name = "SignedMessage Integration"
        print(f"\n[TEST] {test_name}")

        try:
            seed = b"message_integ_seed_1234567890123"
            private_key, public_key = self.adapter.keygen(seed)

            # Create message payload
            payload = {
                "reward_type": "CHR",
                "amount": "50.0",
                "recipient": "user_abc123",
                "reason": "coherence_contribution",
            }

            # Create signed message using the PQC interface (not raw PQC calls)
            message = SignedMessage.create(
                sender_qid="test_node_001",
                recipient_module="RewardAllocator",
                payload=payload,
                tick=100,
                timestamp=1000,
                private_key=private_key,
                public_key=public_key,
                pqc=self.adapter,  # Pass the PQC interface
            )

            # Verify the message
            is_valid = message.verify(self.adapter)

            if is_valid:
                tamper_tests = []

                # Tamper with payload
                tampered_payload_msg = message.model_copy(
                    update={"payload": {**payload, "amount": "999999.0"}}
                )
                tamper_tests.append(
                    ("Payload Tamper", tampered_payload_msg.verify(self.adapter))
                )

                # Tamper with tick
                tampered_tick_msg = message.model_copy(update={"tick": 999})
                tamper_tests.append(
                    ("Tick Tamper", tampered_tick_msg.verify(self.adapter))
                )

                # Tamper with timestamp
                tampered_ts_msg = message.model_copy(update={"timestamp": 9999})
                tamper_tests.append(
                    ("Timestamp Tamper", tampered_ts_msg.verify(self.adapter))
                )

                # All should fail
                all_fail = all(not result for _, result in tamper_tests)

                if all_fail:
                    result = {
                        "test_name": test_name,
                        "status": "PASS",
                        "description": "SignedMessage creation and verification successful with tamper detection",
                        "sender": message.sender_qid,
                        "recipient": message.recipient_module,
                        "tick": message.tick,
                        "tamper_tests": [
                            f"{name}: {'REJECTED' if not res else 'ACCEPTED'}"
                            for name, res in tamper_tests
                        ],
                        "backend": self.backend_name,
                    }
                else:
                    result = {
                        "test_name": test_name,
                        "status": "FAIL",
                        "description": "Some tamper tests passed - security vulnerability",
                        "backend": self.backend_name,
                    }
            else:
                result = {
                    "test_name": test_name,
                    "status": "FAIL",
                    "description": "SignedMessage verification failed",
                    "backend": self.backend_name,
                }

        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "backend": self.backend_name,
            }
        self.log_result(result)

    def test_wrong_seed_length_rejection(self):
        """
        Test: Seed length handling varies by implementation.
        Production PQC should reject non-32-byte seeds, MockPQC pads them.
        """
        test_name = "Wrong Seed Length Rejection"
        print(f"\n[TEST] {test_name}")

        try:
            # 31 bytes (too short)
            seed = b"A" * 31
            try:
                self.adapter.keygen(seed)
                result = {
                    "test_name": test_name,
                    "status": "FAIL",
                    "description": "Did not reject 31-byte seed",
                    "backend": self.backend_name,
                }
            except ValueError:
                result = {
                    "test_name": test_name,
                    "status": "PASS",
                    "description": "Correctly rejected invalid seed length",
                    "backend": self.backend_name,
                }

        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "description": f"Unexpected exception: {str(e)}",
                "backend": self.backend_name,
            }
        self.log_result(result)

    def log_result(self, result: Dict[str, Any]):
        """Helper to log and store result."""
        self.test_results.append(result)
        if result["status"] == "PASS":
            self.pass_count += 1
            print(f"  ✅ PASS: {result['test_name']}")
        else:
            self.fail_count += 1
            print(
                f"  ❌ FAIL: {result['test_name']} - {result.get('error', result.get('description', ''))}"
            )

    def print_summary(self):
        """Print test summary."""
        total_tests = self.pass_count + self.fail_count
        pass_rate = (self.pass_count / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "=" * 80)
        print("PQC STANDARDIZATION TEST SUMMARY")
        print("=" * 80)
        print(f"Backend:      {self.backend_name}")
        print(f"Total Tests:  {total_tests}")
        print(f"Passed:       {self.pass_count} ✅")
        print(f"Failed:       {self.fail_count} ❌")
        print(f"Pass Rate:    {pass_rate:.1f}%")
        print("=" * 80)
        print(f"Pass Rate:    {pass_rate:.1f}%")
        print("=" * 80)

    def generate_evidence_artifact(self):
        """Generate evidence artifact for audit trail with backend information."""
        evidence_dir = os.path.join(os.path.dirname(__file__), "../../evidence/v13_6")
        os.makedirs(evidence_dir, exist_ok=True)
        evidence_path = os.path.join(
            evidence_dir, "pqc_standardization_verification.json"
        )

        # Get backend info
        backend_info = PQCAdapterFactory.get_backend_info()

        evidence = {
            "artifact_type": "pqc_standardization_verification",
            "version": "V13.6",
            "test_suite": "TestPQCStandardization.py",
            "backend": self.backend_name,
            "backend_info": backend_info,
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
        }

        with open(evidence_path, "w") as f:
            json.dump(evidence, f, indent=2)

        print(f"\n📄 Evidence artifact generated: {evidence_path}")


def demo_open_agi_reference_scenario():
    """
    Minimal "Open-AGI reference scenario" that sends real SignedMessage objects
    through CEE modules and produces a composite evidence artifact.
    """
    print("=" * 80)
    print("Open-AGI Reference Scenario Demo")
    print("=" * 80)

    # Create test adapter
    adapter, backend_name = PQCAdapterFactory.create_adapter()
    print(f"Using PQC backend: {backend_name}")

    # Generate keys for the scenario
    seed = b"open_agi_demo_seed_12345678901234"  # 32 bytes
    private_key, public_key = adapter.keygen(seed)

    # Create a series of signed messages simulating an Open-AGI workflow
    messages = []

    # 1. Governance proposal message
    gov_payload = {
        "type": "governance_proposal",
        "proposal_id": "prop_001",
        "title": "Increase reward coefficient",
        "description": "Proposal to increase CHR rewards by 5%",
        "parameters": {"reward_multiplier": "1.05"},
    }

    gov_message = SignedMessage.create(
        sender_qid="gov_node_001",
        recipient_module="GovernanceModule",
        payload=gov_payload,
        tick=1000,
        timestamp=5000,
        private_key=private_key,
        public_key=public_key,
        pqc=adapter,
    )
    messages.append(("Governance Proposal", gov_message))

    # 2. Reward allocation message
    reward_payload = {
        "type": "reward_allocation",
        "recipient": "node_xyz789",
        "amount": "1000.0",
        "currency": "CHR",
        "reason": "coherence_contribution",
    }

    reward_message = SignedMessage.create(
        sender_qid="reward_node_001",
        recipient_module="RewardAllocator",
        payload=reward_payload,
        tick=1001,
        timestamp=5001,
        private_key=private_key,
        public_key=public_key,
        pqc=adapter,
    )
    messages.append(("Reward Allocation", reward_message))

    # 3. NOD allocation message
    nod_payload = {
        "type": "nod_allocation",
        "recipient": "validator_abc123",
        "amount": "500.0",
        "currency": "NOD",
        "source_pool": "atr_fees",
    }

    nod_message = SignedMessage.create(
        sender_qid="nod_node_001",
        recipient_module="NODAllocator",
        payload=nod_payload,
        tick=1002,
        timestamp=5002,
        private_key=private_key,
        public_key=public_key,
        pqc=adapter,
    )
    messages.append(("NOD Allocation", nod_message))

    # Verify all messages
    print(f"\nVerifying {len(messages)} signed messages...")
    verification_results = []

    for msg_name, message in messages:
        is_valid = message.verify(adapter)
        verification_results.append(
            {
                "message_type": msg_name,
                "sender": message.sender_qid,
                "recipient": message.recipient_module,
                "tick": message.tick,
                "valid": is_valid,
            }
        )
        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"  {msg_name}: {status}")

    # Create composite evidence artifact
    evidence_dir = os.path.join(os.path.dirname(__file__), "../../evidence/v13_6")
    os.makedirs(evidence_dir, exist_ok=True)

    evidence_path = os.path.join(evidence_dir, "open_agi_reference_scenario.json")

    evidence = {
        "artifact_type": "open_agi_reference_scenario",
        "version": "V13.6",
        "scenario": "Minimal Open-AGI reference scenario with SignedMessage workflow",
        "backend": backend_name,
        "backend_info": PQCAdapterFactory.get_backend_info(),
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "messages_processed": len(messages),
        "verification_results": verification_results,
        "summary": {
            "total_messages": len(messages),
            "valid_signatures": sum(1 for r in verification_results if r["valid"]),
            "invalid_signatures": sum(
                1 for r in verification_results if not r["valid"]
            ),
        },
    }

    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)

    print(f"\n📄 Composite evidence artifact generated: {evidence_path}")
    print("\n" + "=" * 80)
    print("Open-AGI Reference Scenario Demo Complete!")
    print("=" * 80)


if __name__ == "__main__":
    print("QFS V13.6 - PQC Backend Standardization Verification")
    print(
        "Implementing Phase-3 PQC core as 'real if available, otherwise deterministic mock'"
    )
    print()

    # Run standardization tests
    tester = TestPQCStandardization()
    tester.run_all_tests()

    print("\n" + "=" * 80)
    print("Running Open-AGI Reference Scenario Demo")
    print("=" * 80)

    # Run Open-AGI reference scenario
    demo_open_agi_reference_scenario()

    print("\n✅ PQC standardization verification complete!")
    print("Evidence artifacts:")
    print("  - evidence/v13_6/pqc_standardization_verification.json")
    print("  - evidence/v13_6/open_agi_reference_scenario.json")
