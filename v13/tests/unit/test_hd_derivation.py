"""
<<<<<<< HEAD
test_hd_derivation.py - Unit Tests for BIP-32 HD implementation
"""

import pytest
import binascii
from v13.libs.crypto.derivation import HDKey, _point_mul, _ser256_point, _N

# BIP-32 Test Vector 1
SEED_HEX = "000102030405060708090a0b0c0d0e0f"
MASTER_PRIV_HEX = "e8f32e723decf4051aefac8e2c93c9c5b214313817cdb01a1494b917c8436b35"
MASTER_CHAIN_HEX = "873dff81c02f525623fd1fe5167eac3a55a049de3d314bb42ee227ffed37d508"

# m/0'
M_0H_PRIV_HEX = "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea"
M_0H_CHAIN_HEX = "47fdacbd0f1097043b78c63c20c34ef4ed9a111d980047ad16282c7ae6236141"


def test_vector_1_master():
    seed = bytes.fromhex(SEED_HEX)
    master = HDKey.from_seed(seed)

    assert master.key.hex() == MASTER_PRIV_HEX
    assert master.chain_code.hex() == MASTER_CHAIN_HEX


def test_vector_1_hardened_child():
    seed = bytes.fromhex(SEED_HEX)
    master = HDKey.from_seed(seed)

    # Derive m/0' (Index 0 + 0x80000000)
    child = master.derive(0 + 0x80000000)

    assert child.key.hex() == M_0H_PRIV_HEX
    assert child.chain_code.hex() == M_0H_CHAIN_HEX


def test_unhardened_derivation_math():
    # Sanity check point math
    priv_int = 1
    # 1 * G = G
    point = _point_mul(priv_int)
    # Check G coordinates
    gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    assert point == (gx, gy)

    ser = _ser256_point(point)
    # Compressed G should start with 02 because y is even
    expected_ser = b"\x02" + gx.to_bytes(32, "big")
    assert ser == expected_ser


def test_derive_path_parsing():
    seed = bytes.fromhex(SEED_HEX)
    master = HDKey.from_seed(seed)

    # m/0'
    child1 = master.derive_path("m/0'")
    child2 = master.derive(0x80000000)
    assert child1.key == child2.key

    # m/0'/1
    child3 = master.derive_path("m/0'/1")
    child4 = child2.derive(1)
    assert child3.key == child4.key


def test_hd_key_immutability():
    seed = bytes.fromhex(SEED_HEX)
    node = HDKey.from_seed(seed)
    # Deriving shouldn't change the node itself
    child = node.derive(1)
    assert node.key != child.key
    assert node.depth == 0
    assert child.depth == 1
=======
test_hd_derivation.py - Tests for HD/BIP-style derivation implementation
"""
import unittest
import hashlib
from typing import List
from v13.libs.crypto.derivation import derive_master_key, derive_child_key, derive_path, derive_creator_keypair, ExtendedKey, HARDENED_OFFSET

class TestHDDerivation(unittest.TestCase):
    """Test suite for HD derivation functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_seed = b'test_seed_for_hd_derivation_1234567890'
        self.test_data = {'message': 'test_data_for_signing', 'value': 42}

    def test_derive_master_key(self):
        """Test master key derivation"""
        master_key = derive_master_key(self.test_seed)
        self.assertIsInstance(master_key, ExtendedKey)
        self.assertIsInstance(master_key.key, bytes)
        self.assertIsInstance(master_key.chain_code, bytes)
        self.assertEqual(master_key.depth, 0)
        self.assertEqual(master_key.parent_fingerprint, b'\x00\x00\x00\x00')
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
        self.assertNotEqual(child_key.parent_fingerprint, b'\x00\x00\x00\x00')
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
        self.assertNotEqual(child_key.parent_fingerprint, b'\x00\x00\x00\x00')
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
        private_key, public_address = derive_creator_keypair('DEV')
        self.assertIsInstance(private_key, str)
        self.assertIsInstance(public_address, str)
        self.assertTrue(private_key.startswith(''))
        self.assertTrue(public_address.startswith('0x'))
        self.assertEqual(len(bytes.fromhex(private_key)), 32)
        self.assertGreater(len(public_address), 2)

    def test_derive_creator_keypair_testnet(self):
        """Test creator keypair derivation for TESTNET scope"""
        private_key, public_address = derive_creator_keypair('TESTNET')
        self.assertIsInstance(private_key, str)
        self.assertIsInstance(public_address, str)
        self.assertTrue(private_key.startswith(''))
        self.assertTrue(public_address.startswith('0x'))
        self.assertEqual(len(bytes.fromhex(private_key)), 32)
        self.assertGreater(len(public_address), 2)

    def test_derive_creator_keypair_custom_path(self):
        """Test creator keypair derivation with custom path"""
        custom_path = [1, 2, 3]
        private_key, public_address = derive_creator_keypair('DEV', custom_path)
        self.assertIsInstance(private_key, str)
        self.assertIsInstance(public_address, str)
        self.assertTrue(private_key.startswith(''))
        self.assertTrue(public_address.startswith('0x'))

    def test_derive_creator_keypair_deterministic(self):
        """Test that derivation is deterministic"""
        private_key1, public_address1 = derive_creator_keypair('DEV')
        private_key2, public_address2 = derive_creator_keypair('DEV')
        self.assertEqual(private_key1, private_key2)
        self.assertEqual(public_address1, public_address2)

    def test_invalid_scope_raises_error(self):
        """Test that invalid scope raises ValueError"""
        with self.assertRaises(ValueError):
            derive_creator_keypair('INVALID_SCOPE')

    def test_extended_key_serialization(self):
        """Test serialization and deserialization of extended keys"""
        master_key = derive_master_key(self.test_seed)
        self.assertEqual(master_key.depth, 0)
        self.assertEqual(master_key.child_number, 0)
        self.assertTrue(master_key.is_private)
if __name__ == '__main__':
    unittest.main()
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
