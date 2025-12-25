"""
test_hd_derivation.py - Unit Tests for BIP-32 HD implementation
"""

import unittest
import binascii
from v13.libs.crypto.derivation import (
    HDKey,
    ExtendedKey,
    derive_master_key,
    derive_child_key,
    derive_path,
    derive_creator_keypair,
    HARDENED_OFFSET,
    _point_mul,
    _ser256_point,
    _N,
)

# BIP-32 Test Vector 1
SEED_HEX = "000102030405060708090a0b0c0d0e0f"
MASTER_PRIV_HEX = "e8f32e723decf4051aefac8e2c93c9c5b214313817cdb01a1494b917c8436b35"
MASTER_CHAIN_HEX = "873dff81c02f525623fd1fe5167eac3a55a049de3d314bb42ee227ffed37d508"

# m/0'
M_0H_PRIV_HEX = "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea"
M_0H_CHAIN_HEX = "47fdacbd0f1097043b78c63c20c34ef4ed9a111d980047ad16282c7ae6236141"


class TestHDDerivation(unittest.TestCase):
    """Test suite for HD derivation functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_seed = bytes.fromhex(SEED_HEX)
        self.test_data = {"message": "test_data_for_signing", "value": 42}

    def test_vector_1_master(self):
        """Test master key derivation with BIP-32 Vector 1"""
        master = HDKey.from_seed(self.test_seed)
        self.assertEqual(master.key.hex(), MASTER_PRIV_HEX)
        self.assertEqual(master.chain_code.hex(), MASTER_CHAIN_HEX)

    def test_vector_1_hardened_child(self):
        """Test hardened child key derivation with BIP-32 Vector 1"""
        master = HDKey.from_seed(self.test_seed)
        # Derive m/0' (Index 0 + 0x80000000)
        child = master.derive(0 + HARDENED_OFFSET)
        self.assertEqual(child.key.hex(), M_0H_PRIV_HEX)
        self.assertEqual(child.chain_code.hex(), M_0H_CHAIN_HEX)

    def test_unhardened_derivation_math(self):
        """Sanity check point math for unhardened derivation"""
        priv_int = 1
        # 1 * G = G
        point = _point_mul(priv_int)
        # Check G coordinates
        gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
        self.assertEqual(point, (gx, gy))

        ser = _ser256_point(point)
        # Compressed G should start with 02 because y is even
        expected_ser = b"\x02" + gx.to_bytes(32, "big")
        self.assertEqual(ser, expected_ser)

    def test_derive_path_parsing(self):
        """Test path parsing logic"""
        master = HDKey.from_seed(self.test_seed)
        # m/0'
        child1 = master.derive_path("m/0'")
        child2 = master.derive(0x80000000)
        self.assertEqual(child1.key, child2.key)

        # m/0'/1
        child3 = master.derive_path("m/0'/1")
        child4 = child2.derive(1)
        self.assertEqual(child3.key, child4.key)

    def test_hd_key_immutability(self):
        """Verify that derivation doesn't mutate parent node"""
        node = HDKey.from_seed(self.test_seed)
        child = node.derive(1)
        self.assertNotEqual(node.key, child.key)
        self.assertEqual(node.depth, 0)
        self.assertEqual(child.depth, 1)

    def test_derive_master_key_compat(self):
        """Test compatibility with legacy functional derivation"""
        master_key = derive_master_key(self.test_seed)
        self.assertIsInstance(master_key, ExtendedKey)
        self.assertEqual(len(master_key.key), 32)
        self.assertEqual(master_key.depth, 0)

    def test_derive_creator_keypair_dev(self):
        """Test creator keypair derivation for DEV scope"""
        private_key, public_address = derive_creator_keypair("DEV")
        self.assertIsInstance(private_key, str)
        self.assertIsInstance(public_address, str)
        self.assertTrue(public_address.startswith("qfs1"))
        self.assertEqual(len(bytes.fromhex(private_key)), 32)

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


if __name__ == "__main__":
    unittest.main()
