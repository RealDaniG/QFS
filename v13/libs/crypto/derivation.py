"""
derivation.py - Deterministic BIP-32 HD Wallet Derivation for QFS
Zero-Simulation Compliant | Phase 3 Stage 1
Implements HD/BIP-style derivation tree for enhanced security and organization.
"""

import hashlib
import hmac
import struct
from typing import Tuple, Optional, Union, List
from dataclasses import dataclass

HARDENED_OFFSET = 2147483648
MASTER_KEY_SALT = b"QFS_HD_DERIVATION_MASTER_KEY"
DERIVATION_INFO_PREFIX = b"QFS_HD_DERIVATION|"


@dataclass
class ExtendedKey:
    """Represents an extended key in the HD derivation tree"""

    key: bytes
    chain_code: bytes
    depth: int
    parent_fingerprint: bytes
    child_number: int
    is_private: bool


def hmac_sha512(key: bytes, data: bytes) -> bytes:
    """Compute HMAC-SHA512"""
    return hmac.new(key, data, hashlib.sha512).digest()


# --- Zero-Sim Secp256k1 Minimal Constants ---
# We implement just enough to perform BIP-32 Public Point generation for unhardened derivation.
_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8


def _modinv(a: int, n: int = _P) -> int:
    return pow(a, n - 2, n)


def _point_add(
    p1: Optional[Tuple[int, int]], p2: Optional[Tuple[int, int]]
) -> Optional[Tuple[int, int]]:
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    (x1, y1), (x2, y2) = p1, p2
    if x1 == x2:
        if y1 != y2:
            return None
        # Double
        m = (3 * x1 * x1) * _modinv(2 * y1)
    else:
        # Add
        m = (y2 - y1) * _modinv(x2 - x1)

    m %= _P
    x3 = (m * m - x1 - x2) % _P
    y3 = (m * (x1 - x3) - y1) % _P
    return (x3, y3)


def _point_mul(k: int) -> Optional[Tuple[int, int]]:
    """Scalar multiplication k*G."""
    k %= _N
    # Double-and-add
    curr = (_Gx, _Gy)
    res = None
    for bit in bin(k)[2:]:
        res = _point_add(res, res)
        if bit == "1":
            res = _point_add(res, curr)
    return res


def _ser256_point(p: Optional[Tuple[int, int]]) -> bytes:
    """Serialize point (compressed)."""
    if p is None:
        raise ValueError("Point at infinity")
    x, y = p
    prefix = b"\x02" if y % 2 == 0 else b"\x03"
    return prefix + x.to_bytes(32, "big")


# --- BIP-32 HD Logic ---


class HDKey:
    """
    BIP-32 HD Node (Private only for this implementation scope).
    """

    def __init__(
        self,
        key: bytes,
        chain_code: bytes,
        depth: int,
        index: int,
        parent_fingerprint: bytes,
    ):
        self.key = key  # 32 bytes private key
        self.chain_code = chain_code
        self.depth = depth
        self.index = index
        self.parent_fingerprint = parent_fingerprint

    @classmethod
    def from_seed(cls, seed: bytes) -> "HDKey":
        """Generate master node from seed."""
        I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
        master_key = I[:32]
        chain_code = I[32:]
        return cls(master_key, chain_code, 0, 0, b"\x00\x00\x00\x00")

    def derive(self, index: int) -> "HDKey":
        """Derive child node at index. Index >= 0x80000000 (2^31) is hardened."""
        is_hardened = index >= 0x80000000

        data = b""
        if is_hardened:
            # 0x00 || key || index
            data = b"\x00" + self.key + struct.pack(">I", index)
        else:
            # point(key) || index
            # We need public key point
            k_int = int.from_bytes(self.key, "big")
            point = _point_mul(k_int)
            pub_ser = _ser256_point(point)
            data = pub_ser + struct.pack(">I", index)

        I = hmac.new(self.chain_code, data, hashlib.sha512).digest()
        IL, IR = I[:32], I[32:]

        # Child key = IL + parent_key (mod n)
        il_int = int.from_bytes(IL, "big")
        k_par_int = int.from_bytes(self.key, "big")
        k_child_int = (il_int + k_par_int) % _N

        if il_int >= _N or k_child_int == 0:
            # Incredibly rare invalid key
            return self.derive(
                index + 1
            )  # Skip (very simplified, technically should fail this index)

        child_key = k_child_int.to_bytes(32, "big")
        child_chain = IR

        # We don't strictly calculate legacy fingerprint here to save lines,
        # as we don't need it for QFS internal logic yet.
        return HDKey(child_key, child_chain, self.depth + 1, index, b"\x00" * 4)

    def derive_path(self, path: str) -> "HDKey":
        """Derive from string path e.g. m/44'/9999'/0'/0/0"""
        parts = path.split("/")
        if parts[0] == "m":
            parts = parts[1:]

        node = self
        for part in parts:
            if not part:
                continue
            is_hardened = part.endswith("'")
            idx = int(part[:-1] if is_hardened else part)
            if is_hardened:
                idx += 0x80000000
            node = node.derive(idx)
        return node


# --- QFS System Creator Logic ---

# Development Root Seed (Simulates HSM-injected seed)
# In production, this comes from os.environ or HSM
_DEV_ROOT_SEED = hashlib.sha512(b"QFS_V13_DEV_ROOT_SEED_PHASE_3").digest()

# QFS Coin Type (Private usage 9999')
COIN_TYPE_QFS = 9999


def hkdf_extract(salt: bytes, input_key_material: bytes) -> bytes:
    """HKDF-Extract (RFC 5869)"""
    return hmac.new(salt, input_key_material, hashlib.sha256).digest()


def hkdf_expand(pseudo_random_key: bytes, info: bytes, length: int = 32) -> bytes:
    """HKDF-Expand (RFC 5869)"""
    t = b""
    okm = b""
    i = 0
    while len(okm) < length:
        i += 1
        t = hmac.new(pseudo_random_key, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
    return okm[:length]


def serialize_extended_key(key: ExtendedKey) -> bytes:
    """Serialize an extended key for storage or transmission"""
    result = bytearray()
    result.extend(key.key)
    result.extend(key.chain_code)
    result.append(key.depth)
    result.extend(key.parent_fingerprint)
    result.extend(key.child_number.to_bytes(4, "big"))
    return bytes(result)


def deserialize_extended_key(data: bytes) -> ExtendedKey:
    """Deserialize an extended key from storage or transmission"""
    key = data[:32]
    chain_code = data[32:64]
    depth = data[64]
    parent_fingerprint = data[65:69]
    child_number = int.from_bytes(data[69:73], "big")
    is_private = len(key) == 32
    return ExtendedKey(
        key, chain_code, depth, parent_fingerprint, child_number, is_private
    )


def derive_master_system_key(seed: bytes, scope: str = "DEV") -> Tuple[str, str]:
    """
    Derive the SYSTEM_CREATOR wallet using BIP-44 HD Path and PQC.
    Path: m/44'/{COIN_TYPE_QFS}'/0'/0/0

    The resulting Private Key bytes are used as the SEED for the PQC Provider.
    """
    if scope not in ["DEV", "TESTNET"]:
        raise ValueError("Invalid scope for System Creator derivation")

    # 1. Load Master Node (simulated)
    master = HDKey.from_seed(seed)

    # 2. Derive Path
    # Use Account Index to distinguish Scopes:
    # 0' = DEV
    # 1' = TESTNET
    account_index = 0 if scope == "DEV" else 1

    path = f"m/44'/{COIN_TYPE_QFS}'/{account_index}'/0/0"
    child_node = master.derive_path(path)

    # 3. Use Child Private Key as PQC SEED
    pqc_seed = child_node.key

    # 4. Generate PQC Keypair
    from v13.libs.pqc_provider import get_pqc_provider

    provider = get_pqc_provider()

    # Use Dilithium2 for System Creator keys by default
    pk_bytes, sk_bytes = provider.generate_keypair(pqc_seed, algo_id="dilithium2")

    # 5. Derive Public Address (Hash of PQC PubKey)
    public_key_hash = hashlib.sha256(pk_bytes).digest()
    public_address = "0x" + public_key_hash.hex()

    return sk_bytes.hex(), public_address


def derive_creator_keypair(
    scope: str, path: Optional[List[int]] = None
) -> Tuple[str, str]:
    """
    Derive the SYSTEM_CREATOR wallet keys deterministically using HD derivation.

    Args:
        scope: "DEV" or "TESTNET"
        path: Optional derivation path (defaults to m/44'/9999'/0'/0/0)

    Returns:
        (private_key_hex, public_address)
    """
    if scope not in ("DEV", "TESTNET"):
        raise ValueError(f"Invalid scope: {scope}. Must be 'DEV' or 'TESTNET'.")

    # Use scope-specific seed
    if scope == "DEV":
        seed = _DEV_ROOT_SEED
    else:
        seed = hashlib.sha512(b"QFS_V13_TESTNET_ROOT_SEED").digest()

    # Default path: m/44'/9999'/0'/0/0
    if path is None:
        path = [
            44 + HARDENED_OFFSET,
            COIN_TYPE_QFS + HARDENED_OFFSET,
            0 + HARDENED_OFFSET,
            0,
            0,
        ]

    node = HDKey.from_seed(seed)
    for idx in path:
        node = node.derive(idx)

    private_key_hex = node.key.hex()
    # Simple address: hash of the key
    address_hash = hashlib.sha256(node.key).hexdigest()
    public_address = f"qfs1{address_hash[:40]}"

    return private_key_hex, public_address


# BIP-32 Convenience Wrappers for Legacy Tests
def derive_master_key(seed: bytes) -> ExtendedKey:
    """Derive master extended key from seed (BIP-32 Vector 1 compatible)."""
    node = HDKey.from_seed(seed)
    return ExtendedKey(
        key=node.key,
        chain_code=node.chain_code,
        depth=node.depth,
        parent_fingerprint=node.parent_fingerprint,
        child_number=node.index,
        is_private=True,
    )


def derive_child_key(parent_key: ExtendedKey, index: int) -> ExtendedKey:
    """Derive child extended key from parent."""
    # This is a bit complex as it requires reconstructing HDKey
    node = HDKey(
        parent_key.key,
        parent_key.chain_code,
        parent_key.depth,
        parent_key.child_number,
        parent_key.parent_fingerprint,
    )
    child = node.derive(index)
    return ExtendedKey(
        key=child.key,
        chain_code=child.chain_code,
        depth=child.depth,
        parent_fingerprint=child.parent_fingerprint,
        child_number=child.index,
        is_private=True,
    )


def derive_path(seed: bytes, path: str) -> ExtendedKey:
    """Derive extended key from seed using a path string."""
    master = HDKey.from_seed(seed)
    node = master.derive_path(path)
    return ExtendedKey(
        key=node.key,
        chain_code=node.chain_code,
        depth=node.depth,
        parent_fingerprint=node.parent_fingerprint,
        child_number=node.index,
        is_private=True,
    )


if __name__ == "__main__":
    # Test vector 1 check
    seed = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    m = derive_master_key(seed)
    print(f"Master Key: {m.key.hex()}")
