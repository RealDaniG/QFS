"""
Crypto Abstraction Adapter: Environment-Aware Routing

**Purpose:** Route cryptographic operations to the correct implementation based on environment.

**Routing Decision:**
- `ENV=dev` or `ENV=beta` or `MOCKQPC_ENABLED=true` → MOCKQPC (zero cost, deterministic)
- `ENV=mainnet` AND `MOCKQPC_ENABLED=false` → Real PQC (Dilithium via liboqs)

**CI/CD Guardrails:**
- `CI=true` → Force MOCKQPC, block real PQC (prevent accidental expensive calls in tests)
- Dev/Beta → Raise error if real PQC is attempted
- Mainnet → Require explicit confirmation before activating real PQC

**Contract Compliance:** See ZERO_SIM_QFS_ATLAS_CONTRACT.md § 2.6, § 4.4
"""

import os
from typing import Literal

from v15.crypto.mockqpc import (
    mock_sign_poe,
    mock_verify_poe,
    mock_sign_poe_batch,
    mock_verify_poe_batch,
)

# Environment types
EnvType = Literal["dev", "beta", "mainnet"]


class CryptoConfigError(Exception):
    """Raised when crypto configuration is invalid or unsafe."""

    pass


def _get_env() -> EnvType:
    """
    Get current environment from ENV variable.

    Returns:
        Environment type: "dev", "beta", or "mainnet"

    Raises:
        CryptoConfigError: If ENV is not set or invalid
    """
    env = os.getenv("ENV", "dev").lower()

    if env not in ("dev", "beta", "mainnet"):
        raise CryptoConfigError(
            f"Invalid ENV={env}. Must be 'dev', 'beta', or 'mainnet'. "
            f"Set ENV environment variable before running."
        )

    return env  # type: ignore


def _should_use_mockqpc() -> bool:
    """
    Determine whether to use MOCKQPC or real PQC.

    Decision logic:
    1. If CI=true → Always use MOCKQPC (safety for test environments)
    2. If MOCKQPC_ENABLED=true → Use MOCKQPC
    3. If ENV=dev or ENV=beta → Use MOCKQPC (never real PQC in dev/beta)
    4. If ENV=mainnet AND MOCKQPC_ENABLED=false → Use real PQC

    Returns:
        True if MOCKQPC should be used, False if real PQC should be used

    Raises:
        CryptoConfigError: If configuration is invalid
    """
    # Check if running in CI environment
    if os.getenv("CI", "false").lower() == "true":
        return True

    # Check explicit MOCKQPC_ENABLED flag
    mockqpc_enabled = os.getenv("MOCKQPC_ENABLED", "").lower()
    if mockqpc_enabled == "true":
        return True
    elif mockqpc_enabled == "false":
        # Explicitly disabled, check environment
        env = _get_env()

        # CRITICAL: Never allow real PQC in dev/beta
        if env in ("dev", "beta"):
            raise CryptoConfigError(
                f"Cannot use real PQC in {env} environment. "
                f"Real PQC is only permitted in mainnet. "
                f"Set MOCKQPC_ENABLED=true or ENV=mainnet."
            )

        # Mainnet with MOCKQPC_ENABLED=false → Real PQC
        return False

    # Default: Use MOCKQPC for dev/beta, require explicit flag for mainnet
    env = _get_env()
    if env in ("dev", "beta"):
        return True
    else:
        # Mainnet requires explicit MOCKQPC_ENABLED setting
        raise CryptoConfigError(
            f"ENV=mainnet requires explicit MOCKQPC_ENABLED setting. "
            f"Set MOCKQPC_ENABLED=true (testing) or MOCKQPC_ENABLED=false (production)."
        )


def _real_pqc_sign(data_hash: bytes, env: str) -> bytes:
    """
    Sign using real PQC (Dilithium).

    **WARNING:** This is a stub. Real implementation requires liboqs integration.

    Args:
        data_hash: 32-byte SHA3-256 hash
        env: Environment identifier

    Returns:
        Dilithium signature

    Raises:
        NotImplementedError: Real PQC not yet implemented
    """
    raise NotImplementedError(
        "Real PQC signing not yet implemented. "
        "Requires liboqs/pqcrystals integration. "
        "See ZERO_SIM_MOCKQPC_IMPLEMENTATION.md § Phase 2 for implementation plan."
    )


def _real_pqc_verify(data_hash: bytes, signature: bytes, env: str) -> bool:
    """
    Verify using real PQC (Dilithium).

    **WARNING:** This is a stub. Real implementation requires liboqs integration.

    Args:
        data_hash: 32-byte SHA3-256 hash
        signature: Dilithium signature
        env: Environment identifier

    Returns:
        True if signature is valid

    Raises:
        NotImplementedError: Real PQC not yet implemented
    """
    raise NotImplementedError(
        "Real PQC verification not yet implemented. "
        "Requires liboqs/pqcrystals integration. "
        "See ZERO_SIM_MOCKQPC_IMPLEMENTATION.md § Phase 2 for implementation plan."
    )


def sign_poe(data_hash: bytes, env: str | None = None) -> bytes:
    """
    Sign a Proof-of-Evidence (PoE) data hash.

    **Environment-Aware Routing:**
    - Dev/Beta/CI → MOCKQPC (zero cost, deterministic)
    - Mainnet (when configured) → Real PQC (Dilithium)

    **Usage:**
    ```python
    # Automatic environment detection
    signature = sign_poe(data_hash)

    # Explicit environment (for testing)
    signature = sign_poe(data_hash, env="dev")
    ```

    Args:
        data_hash: 32-byte SHA3-256 hash of the data to sign
        env: Optional environment override (for testing). If None, uses _get_env().

    Returns:
        Signature bytes (size depends on implementation: MOCKQPC=128, Dilithium~3300)

    Raises:
        ValueError: If data_hash is invalid
        CryptoConfigError: If crypto configuration is invalid or unsafe
    """
    # Use provided env or detect from environment
    actual_env = env if env is not None else _get_env()

    # Route to appropriate implementation
    if _should_use_mockqpc():
        return mock_sign_poe(data_hash, actual_env)
    else:
        return _real_pqc_sign(data_hash, actual_env)


def verify_poe(data_hash: bytes, signature: bytes, env: str | None = None) -> bool:
    """
    Verify a Proof-of-Evidence (PoE) signature.

    **Environment-Aware Routing:**
    - Dev/Beta/CI → MOCKQPC (zero cost, deterministic)
    - Mainnet (when configured) → Real PQC (Dilithium)

    Args:
        data_hash: 32-byte SHA3-256 hash of the data
        signature: Signature to verify
        env: Optional environment override (for testing). If None, uses _get_env().

    Returns:
        True if signature is valid, False otherwise

    Raises:
        CryptoConfigError: If crypto configuration is invalid or unsafe
    """
    # Use provided env or detect from environment
    actual_env = env if env is not None else _get_env()

    # Route to appropriate implementation
    if _should_use_mockqpc():
        return mock_verify_poe(data_hash, signature, actual_env)
    else:
        return _real_pqc_verify(data_hash, signature, actual_env)


def sign_poe_batch(data_hashes: list[bytes], env: str | None = None) -> list[bytes]:
    """
    Sign multiple PoE data hashes efficiently.

    Args:
        data_hashes: List of 32-byte SHA3-256 hashes
        env: Optional environment override (for testing)

    Returns:
        List of signatures (same order as input)
    """
    actual_env = env if env is not None else _get_env()

    if _should_use_mockqpc():
        return mock_sign_poe_batch(data_hashes, actual_env)
    else:
        # Real PQC batch signing (stub)
        return [_real_pqc_sign(h, actual_env) for h in data_hashes]


def verify_poe_batch(
    data_hashes: list[bytes], signatures: list[bytes], env: str | None = None
) -> list[bool]:
    """
    Verify multiple PoE signatures efficiently.

    Args:
        data_hashes: List of 32-byte SHA3-256 hashes
        signatures: List of signatures (same order as data_hashes)
        env: Optional environment override (for testing)

    Returns:
        List of verification results (True/False, same order as input)
    """
    actual_env = env if env is not None else _get_env()

    if _should_use_mockqpc():
        return mock_verify_poe_batch(data_hashes, signatures, actual_env)
    else:
        # Real PQC batch verification (stub)
        if len(data_hashes) != len(signatures):
            raise ValueError("data_hashes and signatures must have the same length")
        return [
            _real_pqc_verify(h, s, actual_env) for h, s in zip(data_hashes, signatures)
        ]


def get_crypto_info() -> dict[str, str | bool]:
    """
    Get current crypto configuration info for debugging and auditing.

    Returns:
        Dictionary with crypto configuration details
    """
    env = _get_env()
    use_mockqpc = _should_use_mockqpc()

    return {
        "env": env,
        "use_mockqpc": use_mockqpc,
        "crypto_backend": "MOCKQPC" if use_mockqpc else "Real PQC (Dilithium)",
        "ci_mode": os.getenv("CI", "false").lower() == "true",
        "mockqpc_enabled": os.getenv("MOCKQPC_ENABLED", "auto"),
    }
