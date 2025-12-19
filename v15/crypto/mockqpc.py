"""
MOCKQPC: Deterministic Post-Quantum Cryptography Simulation

**Purpose:** Zero-cost, deterministic simulation of PQC signatures for development and beta environments.

**Guarantees:**
1. Pure functions: Same input → Same output, always.
2. Zero external cost: No API calls, no paid services.
3. Cross-platform determinism: Identical signatures on Windows, macOS, Linux.
4. Zero-Simulation compliant: No randomness, time, network, or filesystem I/O.

**Security Model:**
- MOCKQPC is a SIMULATION, not a cryptographic primitive.
- Security in dev/beta: Environment isolation, not cryptographic strength.
- Mainnet uses real PQC (Dilithium) via the adapter layer.

**Contract Compliance:** See ZERO_SIM_QFS_ATLAS_CONTRACT.md § 4.4
"""

import hashlib
import hmac
from typing import Literal

# Fixed master seed for MOCKQPC (publicly known, intentionally non-secret)
# This is NOT a security vulnerability because MOCKQPC is only for dev/beta.
MOCK_MASTER_SEED = b"QFS_ATLAS_MOCKQPC_v1.4_DETERMINISTIC_SEED"

# Signature size (bytes) to simulate Dilithium Level 3 signatures (~3,300 bytes)
# Using 128 bytes as a reasonable balance for testing
MOCK_SIGNATURE_SIZE = 128

# Environment types
EnvType = Literal["dev", "beta", "mainnet"]


def _hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    """
    HKDF-Expand for deterministic key derivation.

    RFC 5869: HMAC-based Extract-and-Expand Key Derivation Function

    Args:
        prk: Pseudo-random key (from HKDF-Extract)
        info: Context-specific information
        length: Desired output length in bytes

    Returns:
        Derived key material
    """
    hash_len = 64  # SHA-512 output size
    n = (length + hash_len - 1) // hash_len  # Ceiling division

    okm = b""
    t = b""

    for i in range(1, n + 1):
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha512).digest()
        okm += t

    return okm[:length]


def _derive_mock_private_key(env: str) -> bytes:
    """
    Derive a deterministic "private key" for MOCKQPC.

    Uses HKDF with a fixed master seed and environment context.

    Args:
        env: Environment identifier ("dev", "beta", "mainnet")

    Returns:
        64-byte deterministic private key
    """
    # HKDF-Extract: prk = HMAC-SHA512(salt=env, ikm=master_seed)
    salt = env.encode("utf-8")
    prk = hmac.new(salt, MOCK_MASTER_SEED, hashlib.sha512).digest()

    # HKDF-Expand: derive 64 bytes for private key
    info = b"MOCKQPC_PRIVATE_KEY_V1"
    private_key = _hkdf_expand(prk, info, length=64)

    return private_key


def mock_sign_poe(data_hash: bytes, env: str) -> bytes:
    """
    Generate a deterministic MOCKQPC signature for a data hash.

    **Pure Function Contract:**
    - Same (data_hash, env) → Same signature, always
    - No randomness, no time, no network, no filesystem
    - Cross-platform deterministic (Windows, macOS, Linux)

    **Performance:**
    - Execution time: < 1ms
    - External cost: $0

    **Algorithm:**
    1. Derive deterministic private key from env: `sk = HKDF(MASTER_SEED, env)`
    2. Compute signature: `sig = SHA3-512(sk || data_hash || MOCK_TAG)`
    3. Extend to MOCK_SIGNATURE_SIZE using HKDF-Expand

    Args:
        data_hash: SHA3-256 hash of the data to sign (32 bytes)
        env: Environment identifier ("dev", "beta", "mainnet")

    Returns:
        Deterministic signature (MOCK_SIGNATURE_SIZE bytes)

    Raises:
        ValueError: If data_hash is not 32 bytes or env is invalid
    """
    # Validate inputs
    if len(data_hash) != 32:
        raise ValueError(f"data_hash must be 32 bytes (SHA3-256), got {len(data_hash)}")

    if env not in ("dev", "beta", "mainnet"):
        raise ValueError(
            f"Invalid environment: {env}. Must be 'dev', 'beta', or 'mainnet'"
        )

    # Derive deterministic private key
    private_key = _derive_mock_private_key(env)

    # Compute signature base: SHA3-512(private_key || data_hash || tag)
    tag = b"MOCK_PQC_SIG_V1"
    sig_input = private_key + data_hash + tag
    sig_base = hashlib.sha3_512(sig_input).digest()  # 64 bytes

    # Expand to MOCK_SIGNATURE_SIZE using HKDF-Expand
    info = b"MOCKQPC_SIGNATURE_EXPAND_V1" + data_hash
    signature = _hkdf_expand(sig_base, info, length=MOCK_SIGNATURE_SIZE)

    return signature


def mock_verify_poe(data_hash: bytes, signature: bytes, env: str) -> bool:
    """
    Verify a MOCKQPC signature by recomputing and comparing.

    **Pure Function Contract:**
    - Deterministic verification: Same inputs → Same result
    - No randomness, no time, no network, no filesystem

    **Algorithm:**
    1. Recompute expected signature: `expected_sig = mock_sign_poe(data_hash, env)`
    2. Constant-time comparison: `signature == expected_sig`

    Args:
        data_hash: SHA3-256 hash of the data (32 bytes)
        signature: Signature to verify (MOCK_SIGNATURE_SIZE bytes)
        env: Environment identifier ("dev", "beta", "mainnet")

    Returns:
        True if signature is valid, False otherwise
    """
    # Validate signature size
    if len(signature) != MOCK_SIGNATURE_SIZE:
        return False

    try:
        # Recompute expected signature
        expected_signature = mock_sign_poe(data_hash, env)

        # Constant-time comparison (using hmac.compare_digest for timing safety)
        return hmac.compare_digest(signature, expected_signature)

    except ValueError:
        # Invalid data_hash or env
        return False


def mock_sign_poe_batch(data_hashes: list[bytes], env: str) -> list[bytes]:
    """
    Sign multiple data hashes efficiently.

    **Note:** Each signature is still computed independently for determinism.
    This function exists for API convenience, not performance optimization.

    Args:
        data_hashes: List of 32-byte SHA3-256 hashes
        env: Environment identifier

    Returns:
        List of signatures (same order as input)
    """
    return [mock_sign_poe(h, env) for h in data_hashes]


def mock_verify_poe_batch(
    data_hashes: list[bytes], signatures: list[bytes], env: str
) -> list[bool]:
    """
    Verify multiple signatures efficiently.

    Args:
        data_hashes: List of 32-byte SHA3-256 hashes
        signatures: List of signatures (same order as data_hashes)
        env: Environment identifier

    Returns:
        List of verification results (True/False, same order as input)
    """
    if len(data_hashes) != len(signatures):
        raise ValueError("data_hashes and signatures must have the same length")

    return [mock_verify_poe(h, s, env) for h, s in zip(data_hashes, signatures)]
