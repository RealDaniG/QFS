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


def _get_env() -> str:
    """Get current environment (dev, beta, mainnet, ci)."""
    env = os.getenv("QFS_ENV", "dev").lower()
    # Support "ENV" as alias for QFS_ENV to match tests
    if "ENV" in os.environ:
        env = os.environ["ENV"].lower()

    if env not in ["dev", "beta", "mainnet", "ci"]:
        raise CryptoConfigError(f"Invalid ENV: {env}")
    return env


def _is_mockqpc_enabled() -> bool:
    """Check if MOCKQPC is explicitly enabled via env var."""
    return os.getenv("MOCKQPC_ENABLED", "").lower() in ["true", "1", "yes"]


def _is_ci_environment() -> bool:
    """Check if running in CI."""
    return os.getenv("CI", "").lower() in ["true", "1"]


def _should_use_mockqpc(env_override: Optional[str] = None) -> bool:
    """
    Determine whether to use MOCKQPC or real PQC.

    Rules:
    - CI always uses MOCKQPC (forced)
    - Dev always uses MOCKQPC (forced)
    - Beta always uses MOCKQPC (forced)
    - Mainnet uses real PQC UNLESS MOCKQPC_ENABLED=true
    """
    env = env_override if env_override else _get_env()

    if _is_ci_environment() and not env_override:
        return True

    # Check for explicit unsafe configuration in dev/beta
    if env in ["dev", "beta"]:
        # If explicitly disabled in dev/beta, raise error (as per tests)
        mock_enabled_env = os.getenv("MOCKQPC_ENABLED", "").lower()
        if mock_enabled_env == "false":
            raise CryptoConfigError(f"Cannot use real PQC in {env}")
        return True

    if env == "mainnet":
        is_enabled = _is_mockqpc_enabled()
        # Mainnet requires explicit flag to use MOCKQPC, otherwise it defaults to real PQC
        # BUT wait, the test 'test_mainnet_requires_explicit_flag' says:
        # "Verify that mainnet requires explicit MOCKQPC_ENABLED setting"
        # It expects an error if MOCKQPC_ENABLED is NOT set?
        # Let's check the test:
        # with pytest.raises(CryptoConfigError, match="requires explicit MOCKQPC_ENABLED"):
        #    _should_use_mockqpc()
        # So if MOCKQPC_ENABLED is unset in mainnet, we should error?
        # That seems safer than defaulting to Real PQC implicitly?
        # Re-reading the test logic.
        if "MOCKQPC_ENABLED" not in os.environ:
            raise CryptoConfigError("Mainnet requires explicit MOCKQPC_ENABLED setting")

        return is_enabled

    return True  # Safe default


# ============================================================================
# VALIDATION
# ============================================================================


def _validate_pqc_usage(use_real_pqc: bool, env_override: Optional[str] = None):
    """
    Validate that PQC usage is allowed in current environment.

    Raises:
        CryptoConfigError: If trying to use real PQC in unsafe environment
    """
    if not use_real_pqc:
        return  # MOCKQPC is always allowed

    env = env_override if env_override else _get_env()

    if env in ["dev", "beta"]:
        raise CryptoConfigError(f"Cannot use real PQC in {env}")

    if _is_ci_environment() and not env_override:
        # In CI, prevent real PQC unless explicitly overridden for a test
        # The test 'test_ci_prevents_accidental_real_pqc' expects successful *signing* (mock)
        # even if use_real_pqc=True was requested?
        # No, wait.
        # test_ci_prevents_accidental_real_pqc:
        #   calls sign_poe(data_hash) -> default use_real_pqc=False?
        #   The test doesn't pass use_real_pqc=True. It just sets CI=true.
        #   And asserts signature is mock length.
        #   So if use_real_pqc=False (default), this check passes.
        pass

    if _is_ci_environment() and use_real_pqc and not env_override:
        raise CryptoConfigError("Cannot use real PQC in CI")


# ============================================================================
# MOCKQPC IMPLEMENTATION
# ============================================================================


def _mockqpc_sign(data: bytes, env: str) -> bytes:
    """Mock PQC signing (deterministic)."""
    from v15.crypto.mockqpc import mock_sign_poe

    # mock_sign_poe(data_hash, env)
    return mock_sign_poe(data, env)


def _mockqpc_verify(data: bytes, signature: bytes, env: str) -> bool:
    """Mock PQC verification (deterministic)."""
    from v15.crypto.mockqpc import mock_verify_poe

    return mock_verify_poe(data, signature, env)


# ============================================================================
# REAL PQC STUBS
# ============================================================================


def _real_pqc_sign(data: bytes) -> bytes:
    """
    Real PQC signing stub (not implemented).

    Raises:
        NotImplementedError: Always
    """
    raise NotImplementedError("Real PQC signing not yet implemented")


def _real_pqc_verify(data: bytes, signature: bytes) -> bool:
    """
    Real PQC verification stub (not implemented).

    Raises:
        NotImplementedError: Always
    """
    raise NotImplementedError("Real PQC verification not yet implemented")


# ============================================================================
# PUBLIC API
# ============================================================================


def sign_poe(
    data: bytes, use_real_pqc: bool = False, env: Optional[str] = None
) -> bytes:
    """
    Sign Proof-of-Existence data.

    Args:
        data: Data to sign
        use_real_pqc: If True, attempt to use real PQC
        env: Optional override for environment (for testing)

    Returns:
        Signature bytes
    """
    _validate_pqc_usage(use_real_pqc, env_override=env)

    should_use_mock = _should_use_mockqpc(env_override=env)
    current_env = env if env else _get_env()

    if use_real_pqc or not should_use_mock:
        return _real_pqc_sign(data)
    else:
        return _mockqpc_sign(data, current_env)


def verify_poe(
    data: bytes, signature: bytes, use_real_pqc: bool = False, env: Optional[str] = None
) -> bool:
    """
    Verify Proof-of-Existence signature.

    Args:
        data: Original data
        signature: Signature to verify
        use_real_pqc: If True, attempt to use real PQC
        env: Optional override for environment (for testing)

    Returns:
        True if signature is valid

    Raises:
        CryptoConfigError: If trying to use real PQC in unsafe environment
        NotImplementedError: If real PQC is not implemented
    """
    _validate_pqc_usage(use_real_pqc, env_override=env)

    should_use_mock = _should_use_mockqpc(env_override=env)
    current_env = env if env else _get_env()

    if use_real_pqc or not should_use_mock:
        return _real_pqc_verify(data, signature)
    else:
        return _mockqpc_verify(data, signature, current_env)


def sign_poe_batch(data_list: list, use_real_pqc: bool = False) -> list:
    """Batch sign data."""
    return [sign_poe(d, use_real_pqc=use_real_pqc) for d in data_list]


def verify_poe_batch(
    data_list: list, sig_list: list, use_real_pqc: bool = False
) -> list:
    """Batch verify signatures."""
    if len(data_list) != len(sig_list):
        raise ValueError("Data and signature lists must be same length")
    return [
        verify_poe(d, s, use_real_pqc=use_real_pqc) for d, s in zip(data_list, sig_list)
    ]


def get_crypto_info() -> dict:
    """Get current crypto configuration info."""
    return {
        "env": _get_env(),
        "use_mockqpc": _should_use_mockqpc(),
        "mockqpc_enabled": _is_mockqpc_enabled(),
        "ci_mode": _is_ci_environment(),
        "crypto_backend": "MOCKQPC" if _should_use_mockqpc() else "REAL_PQC",
    }
