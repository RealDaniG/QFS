"""
Unit Tests for Crypto Adapter: Environment-Aware Routing

**Test Coverage:**
1. Environment detection and validation
2. MOCKQPC routing for dev/beta/CI
3. Real PQC blocking in dev/beta
4. Configuration error detection
5. Adapter API consistency with MOCKQPC

**Contract Compliance:** ZERO_SIM_QFS_ATLAS_CONTRACT.md § 2.6, § 4.4
"""

import os
import hashlib
import pytest
from unittest.mock import patch

from v15.crypto.adapter import (
    sign_poe,
    verify_poe,
    sign_poe_batch,
    verify_poe_batch,
    get_crypto_info,
    CryptoConfigError,
    _get_env,
    _should_use_mockqpc,
)
from v15.crypto.mockqpc import MOCK_SIGNATURE_SIZE


class TestEnvironmentDetection:
    """Test environment detection logic."""

    def test_default_env_is_dev(self):
        """Verify that default environment is 'dev' when ENV is not set."""
        with patch.dict(os.environ, {}, clear=True):
            env = _get_env()
            assert env == "dev"

    def test_env_detection(self):
        """Verify that ENV variable is correctly detected."""
        with patch.dict(os.environ, {"ENV": "beta"}):
            assert _get_env() == "beta"

        with patch.dict(os.environ, {"ENV": "mainnet"}):
            assert _get_env() == "mainnet"

    def test_env_case_insensitive(self):
        """Verify that ENV detection is case-insensitive."""
        with patch.dict(os.environ, {"ENV": "DEV"}):
            assert _get_env() == "dev"

        with patch.dict(os.environ, {"ENV": "Beta"}):
            assert _get_env() == "beta"

    def test_invalid_env_raises_error(self):
        """Verify that invalid ENV raises CryptoConfigError."""
        with patch.dict(os.environ, {"ENV": "production"}):
            with pytest.raises(CryptoConfigError, match="Invalid ENV"):
                _get_env()


class TestMOCKQPCRouting:
    """Test MOCKQPC vs Real PQC routing logic."""

    def test_ci_forces_mockqpc(self):
        """Verify that CI=true always forces MOCKQPC."""
        with patch.dict(
            os.environ, {"CI": "true", "ENV": "mainnet", "MOCKQPC_ENABLED": "false"}
        ):
            assert _should_use_mockqpc() is True

    def test_mockqpc_enabled_forces_mockqpc(self):
        """Verify that MOCKQPC_ENABLED=true forces MOCKQPC."""
        with patch.dict(os.environ, {"ENV": "mainnet", "MOCKQPC_ENABLED": "true"}):
            assert _should_use_mockqpc() is True

    def test_dev_uses_mockqpc(self):
        """Verify that dev environment uses MOCKQPC."""
        with patch.dict(os.environ, {"ENV": "dev"}, clear=True):
            assert _should_use_mockqpc() is True

    def test_beta_uses_mockqpc(self):
        """Verify that beta environment uses MOCKQPC."""
        with patch.dict(os.environ, {"ENV": "beta"}, clear=True):
            assert _should_use_mockqpc() is True

    def test_dev_blocks_real_pqc(self):
        """Verify that dev environment blocks real PQC even if explicitly requested."""
        with patch.dict(os.environ, {"ENV": "dev", "MOCKQPC_ENABLED": "false"}):
            with pytest.raises(CryptoConfigError, match="Cannot use real PQC in dev"):
                _should_use_mockqpc()

    def test_beta_blocks_real_pqc(self):
        """Verify that beta environment blocks real PQC even if explicitly requested."""
        with patch.dict(os.environ, {"ENV": "beta", "MOCKQPC_ENABLED": "false"}):
            with pytest.raises(CryptoConfigError, match="Cannot use real PQC in beta"):
                _should_use_mockqpc()

    def test_mainnet_requires_explicit_flag(self):
        """Verify that mainnet requires explicit MOCKQPC_ENABLED setting."""
        with patch.dict(os.environ, {"ENV": "mainnet"}, clear=True):
            with pytest.raises(
                CryptoConfigError, match="requires explicit MOCKQPC_ENABLED"
            ):
                _should_use_mockqpc()

    def test_mainnet_with_mockqpc_false_uses_real_pqc(self):
        """Verify that mainnet with MOCKQPC_ENABLED=false attempts real PQC."""
        with patch.dict(os.environ, {"ENV": "mainnet", "MOCKQPC_ENABLED": "false"}):
            assert _should_use_mockqpc() is False


class TestAdapterAPI:
    """Test adapter API functions."""

    def test_sign_poe_uses_mockqpc_in_dev(self):
        """Verify that sign_poe uses MOCKQPC in dev environment."""
        data_hash = hashlib.sha3_256(b"test_data").digest()

        with patch.dict(os.environ, {"ENV": "dev"}, clear=True):
            signature = sign_poe(data_hash)
            assert len(signature) == MOCK_SIGNATURE_SIZE

    def test_verify_poe_uses_mockqpc_in_dev(self):
        """Verify that verify_poe uses MOCKQPC in dev environment."""
        data_hash = hashlib.sha3_256(b"test_data").digest()

        with patch.dict(os.environ, {"ENV": "dev"}, clear=True):
            signature = sign_poe(data_hash)
            assert verify_poe(data_hash, signature) is True

    def test_sign_poe_explicit_env_override(self):
        """Verify that sign_poe accepts explicit env override."""
        data_hash = hashlib.sha3_256(b"test_data").digest()

        # Even if ENV=mainnet, explicit env="dev" should work
        with patch.dict(os.environ, {"ENV": "mainnet", "MOCKQPC_ENABLED": "true"}):
            sig_dev = sign_poe(data_hash, env="dev")
            sig_beta = sign_poe(data_hash, env="beta")

            # Different envs should produce different signatures
            assert sig_dev != sig_beta

    def test_adapter_determinism(self):
        """Verify that adapter maintains MOCKQPC determinism."""
        data_hash = hashlib.sha3_256(b"test_data").digest()

        with patch.dict(os.environ, {"ENV": "dev"}, clear=True):
            # Sign multiple times
            signatures = [sign_poe(data_hash) for _ in range(10)]

            # All should be identical
            assert len(set(signatures)) == 1

    def test_sign_poe_batch(self):
        """Verify that batch signing works through adapter."""
        hashes = [hashlib.sha3_256(f"data{i}".encode()).digest() for i in range(5)]

        with patch.dict(os.environ, {"ENV": "dev"}, clear=True):
            sigs = sign_poe_batch(hashes)
            assert len(sigs) == 5
            assert all(len(s) == MOCK_SIGNATURE_SIZE for s in sigs)

    def test_verify_poe_batch(self):
        """Verify that batch verification works through adapter."""
        hashes = [hashlib.sha3_256(f"data{i}".encode()).digest() for i in range(5)]

        with patch.dict(os.environ, {"ENV": "dev"}, clear=True):
            sigs = sign_poe_batch(hashes)
            results = verify_poe_batch(hashes, sigs)

            assert len(results) == 5
            assert all(results)

    def test_real_pqc_stub_raises_not_implemented(self):
        """Verify that real PQC operations raise NotImplementedError."""
        data_hash = hashlib.sha3_256(b"test").digest()

        with patch.dict(os.environ, {"ENV": "mainnet", "MOCKQPC_ENABLED": "false"}):
            with pytest.raises(
                NotImplementedError, match="Real PQC signing not yet implemented"
            ):
                sign_poe(data_hash)


class TestCryptoInfo:
    """Test crypto configuration info."""

    def test_get_crypto_info_dev(self):
        """Verify crypto info in dev environment."""
        with patch.dict(os.environ, {"ENV": "dev"}, clear=True):
            info = get_crypto_info()

            assert info["env"] == "dev"
            assert info["use_mockqpc"] is True
            assert info["crypto_backend"] == "MOCKQPC"
            assert info["ci_mode"] is False

    def test_get_crypto_info_ci(self):
        """Verify crypto info in CI environment."""
        with patch.dict(
            os.environ, {"ENV": "mainnet", "CI": "true", "MOCKQPC_ENABLED": "false"}
        ):
            info = get_crypto_info()

            assert info["ci_mode"] is True
            assert info["use_mockqpc"] is True  # CI forces MOCKQPC
            assert info["crypto_backend"] == "MOCKQPC"


class TestAdapterSafety:
    """Test safety guardrails in adapter."""

    def test_ci_prevents_accidental_real_pqc(self):
        """Verify that CI=true prevents accidental real PQC usage."""
        data_hash = hashlib.sha3_256(b"test").digest()

        # Even with ENV=mainnet and MOCKQPC_ENABLED=false, CI=true should force MOCKQPC
        with patch.dict(
            os.environ, {"ENV": "mainnet", "MOCKQPC_ENABLED": "false", "CI": "true"}
        ):
            # Should use MOCKQPC, not raise NotImplementedError
            signature = sign_poe(data_hash)
            assert len(signature) == MOCK_SIGNATURE_SIZE

    def test_dev_safety_guard(self):
        """Verify that dev environment never allows real PQC."""
        with patch.dict(os.environ, {"ENV": "dev", "MOCKQPC_ENABLED": "false"}):
            with pytest.raises(CryptoConfigError, match="Cannot use real PQC in dev"):
                _should_use_mockqpc()
