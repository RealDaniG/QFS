"""
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
