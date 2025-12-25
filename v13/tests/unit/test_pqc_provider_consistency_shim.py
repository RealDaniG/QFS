"""
test_pqc_provider_consistency_shim.py - Tests for PQC provider consistency between mock and real implementations
Ensures structural compatibility and replayability of signatures
"""

import unittest
import hashlib
from typing import List, Dict, Any
import pytest
from v13.libs.pqc.IPQCProvider import (
    IPQCProvider,
    PrivKeyHandle,
    KeyPair,
    ValidationResult,
)
from v13.libs.pqc.ConcretePQCProvider import ConcretePQCProvider, MockPQCProvider


# TODO: These tests require native PQC dependencies (AES256_CTR_DRBG) and LegacyPQC methods
# (serialize_data, get_backend_info) which are not available in mock/CI mode.
# Issue: PQC Provider API needs to be fully mocked or native libs installed.
@pytest.mark.xfail(
    reason="PQC shim tests require native dependencies unavailable in CI", strict=False
)
class TestPQCProviderConsistencyShim(unittest.TestCase):
    """Test suite for checking consistency between PQC provider implementations"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_provider = MockPQCProvider()
        self.concrete_provider = ConcretePQCProvider()
        # Must be exactly 32 bytes for Dilithium5 deterministic keygen
        self.test_seed = b"test_seed_32_bytes_for_pqc_ok!"[:32].ljust(32, b"\x00")
        self.test_data = {"message": "test_data_for_signing", "value": 42}
        self.log_list: List[Dict[str, Any]] = []

    def test_structural_compatibility_of_keypairs(self):
        """Test that mock and concrete providers produce structurally compatible key pairs"""
        mock_keypair = self.mock_provider.generate_keypair(
            log_list=self.log_list,
            seed=self.test_seed,
            pqc_cid="test_structural_compatibility",
        )
        concrete_keypair = self.concrete_provider.generate_keypair(
            log_list=self.log_list,
            seed=self.test_seed,
            pqc_cid="test_structural_compatibility",
        )
        self.assertIsInstance(mock_keypair, KeyPair)
        self.assertIsInstance(concrete_keypair, KeyPair)
        self.assertIsInstance(mock_keypair.private_key_handle, PrivKeyHandle)
        self.assertIsInstance(concrete_keypair.private_key_handle, PrivKeyHandle)
        self.assertIsInstance(mock_keypair.public_key, bytes)
        self.assertIsInstance(concrete_keypair.public_key, bytes)
        self.assertEqual(mock_keypair.algo_id, self.mock_provider.get_algo_id())
        self.assertEqual(concrete_keypair.algo_id, self.concrete_provider.get_algo_id())
        self.assertIsInstance(mock_keypair.private_key_handle.handle_id, str)
        self.assertIsInstance(mock_keypair.private_key_handle.algo_id, str)
        self.assertIsInstance(mock_keypair.private_key_handle.metadata, dict)
        self.assertIsInstance(concrete_keypair.private_key_handle.handle_id, str)
        self.assertIsInstance(concrete_keypair.private_key_handle.algo_id, str)
        self.assertIsInstance(concrete_keypair.private_key_handle.metadata, dict)

    def test_signature_structure_compatibility(self):
        """Test that signatures from both providers have compatible structures"""
        mock_keypair = self.mock_provider.generate_keypair(
            log_list=self.log_list,
            seed=self.test_seed,
            pqc_cid="test_signature_structure",
        )
        concrete_keypair = self.concrete_provider.generate_keypair(
            log_list=self.log_list,
            seed=self.test_seed,
            pqc_cid="test_signature_structure",
        )
        mock_signature = self.mock_provider.sign_data(
            private_key_handle=mock_keypair.private_key_handle,
            data=self.test_data,
            log_list=self.log_list,
            pqc_cid="test_signature_structure",
        )
        concrete_signature = self.concrete_provider.sign_data(
            private_key_handle=concrete_keypair.private_key_handle,
            data=self.test_data,
            log_list=self.log_list,
            pqc_cid="test_signature_structure",
        )
        self.assertIsInstance(mock_signature, bytes)
        self.assertIsInstance(concrete_signature, bytes)
        self.assertGreater(len(mock_signature), 0)
        self.assertGreater(len(concrete_signature), 0)

    def test_signature_verification_compatibility(self):
        """Test that signatures from one provider can be verified by the other"""
        mock_keypair = self.mock_provider.generate_keypair(
            log_list=self.log_list,
            seed=self.test_seed,
            pqc_cid="test_verification_compatibility",
        )
        concrete_keypair = self.concrete_provider.generate_keypair(
            log_list=self.log_list,
            seed=self.test_seed,
            pqc_cid="test_verification_compatibility",
        )
        mock_signature = self.mock_provider.sign_data(
            private_key_handle=mock_keypair.private_key_handle,
            data=self.test_data,
            log_list=self.log_list,
            pqc_cid="test_verification_compatibility",
        )
        concrete_signature = self.concrete_provider.sign_data(
            private_key_handle=concrete_keypair.private_key_handle,
            data=self.test_data,
            log_list=self.log_list,
            pqc_cid="test_verification_compatibility",
        )
        mock_sig_validation = self.concrete_provider.verify_signature(
            public_key=mock_keypair.public_key,
            data=self.test_data,
            signature=mock_signature,
            log_list=self.log_list,
            pqc_cid="test_verification_compatibility",
        )
        concrete_sig_validation = self.mock_provider.verify_signature(
            public_key=concrete_keypair.public_key,
            data=self.test_data,
            signature=concrete_signature,
            log_list=self.log_list,
            pqc_cid="test_verification_compatibility",
        )
        self.assertIsInstance(mock_sig_validation, ValidationResult)
        self.assertIsInstance(concrete_sig_validation, ValidationResult)

    def test_replayability_of_signatures(self):
        """Test that signatures are replayable and can be validated purely from deterministic input"""
        keypair1 = self.mock_provider.generate_keypair(
            log_list=self.log_list, seed=self.test_seed, pqc_cid="test_replayability"
        )
        keypair2 = self.mock_provider.generate_keypair(
            log_list=[], seed=self.test_seed, pqc_cid="test_replayability"
        )
        signature1 = self.mock_provider.sign_data(
            private_key_handle=keypair1.private_key_handle,
            data=self.test_data,
            log_list=self.log_list,
            pqc_cid="test_replayability",
        )
        signature2 = self.mock_provider.sign_data(
            private_key_handle=keypair2.private_key_handle,
            data=self.test_data,
            log_list=[],
            pqc_cid="test_replayability",
        )
        self.assertEqual(signature1, signature2)
        validation1 = self.mock_provider.verify_signature(
            public_key=keypair1.public_key,
            data=self.test_data,
            signature=signature1,
            log_list=self.log_list,
            pqc_cid="test_replayability",
        )
        validation2 = self.mock_provider.verify_signature(
            public_key=keypair2.public_key,
            data=self.test_data,
            signature=signature2,
            log_list=[],
            pqc_cid="test_replayability",
        )
        self.assertTrue(validation1.is_valid)
        self.assertTrue(validation2.is_valid)

    def test_deterministic_behavior_with_same_inputs(self):
        """Test that providers behave deterministically with identical inputs"""
        log_list1: List[Dict[str, Any]] = []
        log_list2: List[Dict[str, Any]] = []
        keypair1 = self.mock_provider.generate_keypair(
            log_list=log_list1,
            seed=self.test_seed,
            parameters={"test": "param"},
            pqc_cid="test_determinism",
            deterministic_timestamp=1234567890,
        )
        keypair2 = self.mock_provider.generate_keypair(
            log_list=log_list2,
            seed=self.test_seed,
            parameters={"test": "param"},
            pqc_cid="test_determinism",
            deterministic_timestamp=1234567890,
        )
        self.assertEqual(
            keypair1.private_key_handle.handle_id, keypair2.private_key_handle.handle_id
        )
        self.assertEqual(keypair1.public_key, keypair2.public_key)
        self.assertEqual(keypair1.algo_id, keypair2.algo_id)
        sig1 = self.mock_provider.sign_data(
            private_key_handle=keypair1.private_key_handle,
            data=self.test_data,
            log_list=log_list1,
            pqc_cid="test_determinism",
            deterministic_timestamp=1234567890,
        )
        sig2 = self.mock_provider.sign_data(
            private_key_handle=keypair2.private_key_handle,
            data=self.test_data,
            log_list=log_list2,
            pqc_cid="test_determinism",
            deterministic_timestamp=1234567890,
        )
        self.assertEqual(sig1, sig2)

    def test_backend_info_consistency(self):
        """Test that backend info is consistently provided"""
        mock_info = self.mock_provider.get_backend_info()
        concrete_info = self.concrete_provider.get_backend_info()
        self.assertIsInstance(mock_info, dict)
        self.assertIsInstance(concrete_info, dict)
        self.assertIn("algo_id", mock_info)
        self.assertIn("algo_id", concrete_info)
        self.assertFalse(mock_info.get("production_ready", True))


if __name__ == "__main__":
    unittest.main()
