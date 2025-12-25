"""
Crypto adapter for PQC and MOCKQPC.
Provides environment-aware routing between mock and real PQC.
"""

import os
from typing import Optional


# ============================================================================
# EXCEPTIONS
# ============================================================================


class CryptoConfigError(Exception):
    """Raised when crypto configuration is invalid or unsafe."""

    pass


# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================


def _get_environment() -> str:
    """Get current environment (dev, beta, mainnet, ci)."""
    env = os.getenv("QFS_ENV", "dev").lower()
    if env not in ["dev", "beta", "mainnet", "ci"]:
        raise CryptoConfigError(f"Invalid environment: {env}")
    return env


def _is_mockqpc_enabled() -> bool:
    """Check if MOCKQPC is explicitly enabled via env var."""
    return os.getenv("MOCKQPC_ENABLED", "").lower() in ["true", "1", "yes"]


def _is_ci_environment() -> bool:
    """Check if running in CI."""
    return os.getenv("CI", "").lower() in ["true", "1"]


def _should_use_mockqpc() -> bool:
    """
    Determine whether to use MOCKQPC or real PQC.

    Rules:
    - CI always uses MOCKQPC (forced)
    - Dev always uses MOCKQPC (forced)
    - Beta always uses MOCKQPC (forced)
    - Mainnet uses real PQC UNLESS MOCKQPC_ENABLED=true
    """
    env = _get_environment()

    if _is_ci_environment():
        return True

    if env in ["dev", "beta"]:
        return True

    if env == "mainnet":
        return _is_mockqpc_enabled()

    return True  # Safe default


# ============================================================================
# VALIDATION
# ============================================================================


def _validate_pqc_usage(use_real_pqc: bool = False):
    """
    Validate that PQC usage is allowed in current environment.

    Raises:
        CryptoConfigError: If trying to use real PQC in unsafe environment
    """
    if not use_real_pqc:
        return  # MOCKQPC is always allowed

    env = _get_environment()

    if env in ["dev", "beta"]:
        raise CryptoConfigError(f"Cannot use real PQC in {env}")

    if _is_ci_environment():
        raise CryptoConfigError("Cannot use real PQC in CI")


# ============================================================================
# MOCKQPC IMPLEMENTATION
# ============================================================================


def _mockqpc_sign(data: bytes) -> bytes:
    """Mock PQC signing (deterministic)."""
    import hashlib

    return hashlib.sha256(b"mock_sign:" + data).digest()


def _mockqpc_verify(data: bytes, signature: bytes) -> bool:
    """Mock PQC verification (deterministic)."""
    expected = _mockqpc_sign(data)
    return expected == signature


# ============================================================================
# REAL PQC STUBS
# ============================================================================


def _real_pqc_sign(data: bytes) -> bytes:
    """
    Real PQC signing stub (not implemented).

    Raises:
        NotImplementedError: Always
    """
    raise NotImplementedError("Real PQC implementation not available yet")


def _real_pqc_verify(data: bytes, signature: bytes) -> bool:
    """
    Real PQC verification stub (not implemented).

    Raises:
        NotImplementedError: Always
    """
    raise NotImplementedError("Real PQC implementation not available yet")


# ============================================================================
# PUBLIC API
# ============================================================================


def sign_poe(data: bytes, use_real_pqc: bool = False) -> bytes:
    """
    Sign Proof-of-Existence data.

    Args:
        data: Data to sign
        use_real_pqc: If True, attempt to use real PQC

    Returns:
        Signature bytes

    Raises:
        CryptoConfigError: If trying to use real PQC in unsafe environment
        NotImplementedError: If real PQC is not implemented
    """
    _validate_pqc_usage(use_real_pqc)

    should_use_mock = _should_use_mockqpc()

    if use_real_pqc and not should_use_mock:
        return _real_pqc_sign(data)
    else:
        return _mockqpc_sign(data)


def verify_poe(data: bytes, signature: bytes, use_real_pqc: bool = False) -> bool:
    """
    Verify Proof-of-Existence signature.

    Args:
        data: Original data
        signature: Signature to verify
        use_real_pqc: If True, attempt to use real PQC

    Returns:
        True if signature is valid

    Raises:
        CryptoConfigError: If trying to use real PQC in unsafe environment
        NotImplementedError: If real PQC is not implemented
    """
    _validate_pqc_usage(use_real_pqc)

    should_use_mock = _should_use_mockqpc()

    if use_real_pqc and not should_use_mock:
        return _real_pqc_verify(data, signature)
    else:
        return _mockqpc_verify(data, signature)


def get_crypto_info() -> dict:
    """Get current crypto configuration info."""
    return {
        "environment": _get_environment(),
        "using_mockqpc": _should_use_mockqpc(),
        "mockqpc_enabled": _is_mockqpc_enabled(),
        "is_ci": _is_ci_environment(),
    }
