"""
test_hd_derivation.py - Tests for HD/BIP-style derivation implementation
"""

import unittest
import hashlib
from typing import List
from v13.libs.crypto.derivation import (
    derive_master_key,
    derive_child_key,
    derive_path,
    derive_creator_keypair,
    ExtendedKey,
    HARDENED_OFFSET,
)


class TestHDDerivation(unittest.TestCase):
    """Test suite for HD derivation functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_seed = b"test_seed_for_hd_derivation_1234567890"
        self.test_data = {"message": "test_data_for_signing", "value": 42}

    def test_derive_master_key(self):
        """Test master key derivation"""
        master_key = derive_master_key(self.test_seed)
        self.assertIsInstance(master_key, ExtendedKey)
        self.assertIsInstance(master_key.key, bytes)
        self.assertIsInstance(master_key.chain_code, bytes)
        self.assertEqual(master_key.depth, 0)
        self.assertEqual(master_key.parent_fingerprint, b"\x00\x00\x00\x00")
        self.assertEqual(master_key.child_number, 0)
        self.assertTrue(master_key.is_private)
        self.assertEqual(len(master_key.key), 32)
        self.assertEqual(len(master_key.chain_code), 32)

    def test_derive_child_key_normal(self):
        """Test normal child key derivation"""
        master_key = derive_master_key(self.test_seed)
        child_key = derive_child_key(master_key, 0)
        self.assertIsInstance(child_key, ExtendedKey)
        self.assertIsInstance(child_key.key, bytes)
        self.assertIsInstance(child_key.chain_code, bytes)
        self.assertEqual(child_key.depth, 1)
        self.assertNotEqual(child_key.parent_fingerprint, b"\x00\x00\x00\x00")
        self.assertEqual(child_key.child_number, 0)
        self.assertTrue(child_key.is_private)
        self.assertNotEqual(child_key.key, master_key.key)
        self.assertNotEqual(child_key.chain_code, master_key.chain_code)

    def test_derive_child_key_hardened(self):
        """Test hardened child key derivation"""
        master_key = derive_master_key(self.test_seed)
        child_key = derive_child_key(master_key, 0 + HARDENED_OFFSET)
        self.assertIsInstance(child_key, ExtendedKey)
        self.assertIsInstance(child_key.key, bytes)
        self.assertIsInstance(child_key.chain_code, bytes)
        self.assertEqual(child_key.depth, 1)
        self.assertNotEqual(child_key.parent_fingerprint, b"\x00\x00\x00\x00")
        self.assertEqual(child_key.child_number, 0 + HARDENED_OFFSET)
        self.assertTrue(child_key.is_private)

    def test_derive_path(self):
        """Test derivation of a full path"""
        master_key = derive_master_key(self.test_seed)
        path = [0, 1, 2]
        derived_key = derive_path(master_key, path)
        self.assertIsInstance(derived_key, ExtendedKey)
        self.assertEqual(derived_key.depth, len(path))
        self.assertNotEqual(derived_key.key, master_key.key)

    def test_derive_creator_keypair_dev(self):
        """Test creator keypair derivation for DEV scope"""
        private_key, public_address = derive_creator_keypair("DEV")
        self.assertIsInstance(private_key, str)
        self.assertIsInstance(public_address, str)
        self.assertTrue(private_key.startswith(""))
        self.assertTrue(public_address.startswith("0x"))
        self.assertEqual(len(bytes.fromhex(private_key)), 32)
        self.assertGreater(len(public_address), 2)

    def test_derive_creator_keypair_testnet(self):
        """Test creator keypair derivation for TESTNET scope"""
        private_key, public_address = derive_creator_keypair("TESTNET")
        self.assertIsInstance(private_key, str)
        self.assertIsInstance(public_address, str)
        self.assertTrue(private_key.startswith(""))
        self.assertTrue(public_address.startswith("0x"))
        self.assertEqual(len(bytes.fromhex(private_key)), 32)
        self.assertGreater(len(public_address), 2)

    def test_derive_creator_keypair_custom_path(self):
        """Test creator keypair derivation with custom path"""
        custom_path = [1, 2, 3]
        private_key, public_address = derive_creator_keypair("DEV", custom_path)
        self.assertIsInstance(private_key, str)
        self.assertIsInstance(public_address, str)
        self.assertTrue(private_key.startswith(""))
        self.assertTrue(public_address.startswith("0x"))

    def test_derive_creator_keypair_deterministic(self):
        """Test that derivation is deterministic"""
        private_key1, public_address1 = derive_creator_keypair("DEV")
        private_key2, public_address2 = derive_creator_keypair("DEV")
        self.assertEqual(private_key1, private_key2)
        self.assertEqual(public_address1, public_address2)

    def test_invalid_scope_raises_error(self):
        """Test that invalid scope raises ValueError"""
        with self.assertRaises(ValueError):
            derive_creator_keypair("INVALID_SCOPE")

    def test_extended_key_serialization(self):
        """Test serialization and deserialization of extended keys"""
        master_key = derive_master_key(self.test_seed)
        self.assertEqual(master_key.depth, 0)
        self.assertEqual(master_key.child_number, 0)
        self.assertTrue(master_key.is_private)


if __name__ == "__main__":
    unittest.main()
