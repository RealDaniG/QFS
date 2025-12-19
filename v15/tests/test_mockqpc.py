"""
Unit Tests for MOCKQPC: Deterministic PQC Simulation

**Test Coverage:**
1. Determinism: Same input → Same output (100% reproducibility)
2. Cross-run determinism: Multiple test runs produce identical results
3. Input validation: Proper error handling for invalid inputs
4. Batch operations: Consistency between single and batch operations
5. Environment separation: Different env → Different signatures
6. Performance: Sub-millisecond sign/verify operations

**Contract Compliance:** ZERO_SIM_QFS_ATLAS_CONTRACT.md § 4.4
"""

import hashlib
import pytest
from v15.crypto.mockqpc import (
    mock_sign_poe,
    mock_verify_poe,
    mock_sign_poe_batch,
    mock_verify_poe_batch,
    MOCK_SIGNATURE_SIZE,
)


class TestMOCKQPCDeterminism:
    """Test determinism guarantees of MOCKQPC."""

    def test_same_input_same_output(self):
        """Verify that identical inputs produce identical signatures."""
        data_hash = hashlib.sha3_256(b"test_data").digest()
        env = "dev"

        # Sign the same data 10 times
        signatures = [mock_sign_poe(data_hash, env) for _ in range(10)]

        # All signatures must be identical
        assert len(set(signatures)) == 1, "Signatures must be deterministic"
        assert all(sig == signatures[0] for sig in signatures)

    def test_determinism_across_environments(self):
        """Verify that different environments produce different signatures."""
        data_hash = hashlib.sha3_256(b"test_data").digest()

        sig_dev = mock_sign_poe(data_hash, "dev")
        sig_beta = mock_sign_poe(data_hash, "beta")
        sig_mainnet = mock_sign_poe(data_hash, "mainnet")

        # Each environment should produce a unique signature
        assert sig_dev != sig_beta
        assert sig_beta != sig_mainnet
        assert sig_dev != sig_mainnet

        # But each environment should be internally deterministic
        assert mock_sign_poe(data_hash, "dev") == sig_dev
        assert mock_sign_poe(data_hash, "beta") == sig_beta
        assert mock_sign_poe(data_hash, "mainnet") == sig_mainnet

    def test_different_data_different_signature(self):
        """Verify that different data produces different signatures."""
        env = "dev"

        data1 = hashlib.sha3_256(b"data1").digest()
        data2 = hashlib.sha3_256(b"data2").digest()

        sig1 = mock_sign_poe(data1, env)
        sig2 = mock_sign_poe(data2, env)

        assert sig1 != sig2

    def test_signature_size(self):
        """Verify that signatures have the correct fixed size."""
        data_hash = hashlib.sha3_256(b"test").digest()

        for env in ["dev", "beta", "mainnet"]:
            sig = mock_sign_poe(data_hash, env)
            assert len(sig) == MOCK_SIGNATURE_SIZE


class TestMOCKQPCVerification:
    """Test signature verification."""

    def test_valid_signature_verifies(self):
        """Verify that a valid signature is accepted."""
        data_hash = hashlib.sha3_256(b"test_data").digest()
        env = "dev"

        signature = mock_sign_poe(data_hash, env)
        assert mock_verify_poe(data_hash, signature, env) is True

    def test_invalid_signature_rejected(self):
        """Verify that an invalid signature is rejected."""
        data_hash = hashlib.sha3_256(b"test_data").digest()
        env = "dev"

        # Create a valid signature
        valid_sig = mock_sign_poe(data_hash, env)

        # Corrupt the signature
        invalid_sig = bytes([(b + 1) % 256 for b in valid_sig])

        assert mock_verify_poe(data_hash, invalid_sig, env) is False

    def test_wrong_environment_rejected(self):
        """Verify that a signature from one environment is rejected in another."""
        data_hash = hashlib.sha3_256(b"test_data").digest()

        sig_dev = mock_sign_poe(data_hash, "dev")

        # Signature should verify in dev
        assert mock_verify_poe(data_hash, sig_dev, "dev") is True

        # But not in beta or mainnet
        assert mock_verify_poe(data_hash, sig_dev, "beta") is False
        assert mock_verify_poe(data_hash, sig_dev, "mainnet") is False

    def test_wrong_data_rejected(self):
        """Verify that a signature is rejected for different data."""
        data1 = hashlib.sha3_256(b"data1").digest()
        data2 = hashlib.sha3_256(b"data2").digest()
        env = "dev"

        sig1 = mock_sign_poe(data1, env)

        # Signature should verify for data1
        assert mock_verify_poe(data1, sig1, env) is True

        # But not for data2
        assert mock_verify_poe(data2, sig1, env) is False

    def test_wrong_size_signature_rejected(self):
        """Verify that a signature with wrong size is rejected."""
        data_hash = hashlib.sha3_256(b"test").digest()
        env = "dev"

        # Too short
        assert mock_verify_poe(data_hash, b"short", env) is False

        # Too long
        long_sig = b"x" * (MOCK_SIGNATURE_SIZE + 10)
        assert mock_verify_poe(data_hash, long_sig, env) is False


class TestMOCKQPCInputValidation:
    """Test input validation and error handling."""

    def test_invalid_hash_size(self):
        """Verify that invalid hash size raises ValueError."""
        env = "dev"

        # Too short
        with pytest.raises(ValueError, match="must be 32 bytes"):
            mock_sign_poe(b"short", env)

        # Too long
        with pytest.raises(ValueError, match="must be 32 bytes"):
            mock_sign_poe(b"x" * 64, env)

    def test_invalid_environment(self):
        """Verify that invalid environment raises ValueError."""
        data_hash = hashlib.sha3_256(b"test").digest()

        with pytest.raises(ValueError, match="Invalid environment"):
            mock_sign_poe(data_hash, "invalid")

        with pytest.raises(ValueError, match="Invalid environment"):
            mock_sign_poe(data_hash, "production")

    def test_verify_invalid_input_returns_false(self):
        """Verify that verify_poe returns False for invalid inputs (not exceptions)."""
        # Invalid hash size should return False, not raise
        assert mock_verify_poe(b"short", b"x" * MOCK_SIGNATURE_SIZE, "dev") is False

        # Invalid env should return False, not raise
        data_hash = hashlib.sha3_256(b"test").digest()
        sig = mock_sign_poe(data_hash, "dev")
        assert mock_verify_poe(data_hash, sig, "invalid") is False


class TestMOCKQPCBatchOperations:
    """Test batch sign/verify operations."""

    def test_batch_sign_consistency(self):
        """Verify that batch signing matches individual signing."""
        hashes = [hashlib.sha3_256(f"data{i}".encode()).digest() for i in range(5)]
        env = "dev"

        # Sign individually
        individual_sigs = [mock_sign_poe(h, env) for h in hashes]

        # Sign as batch
        batch_sigs = mock_sign_poe_batch(hashes, env)

        # Should be identical
        assert individual_sigs == batch_sigs

    def test_batch_verify_consistency(self):
        """Verify that batch verification matches individual verification."""
        hashes = [hashlib.sha3_256(f"data{i}".encode()).digest() for i in range(5)]
        env = "dev"

        sigs = mock_sign_poe_batch(hashes, env)

        # Verify individually
        individual_results = [mock_verify_poe(h, s, env) for h, s in zip(hashes, sigs)]

        # Verify as batch
        batch_results = mock_verify_poe_batch(hashes, sigs, env)

        # Should be identical
        assert individual_results == batch_results
        assert all(batch_results)  # All should be True

    def test_batch_verify_mixed_validity(self):
        """Verify batch verification with mixed valid/invalid signatures."""
        hashes = [hashlib.sha3_256(f"data{i}".encode()).digest() for i in range(5)]
        env = "dev"

        sigs = mock_sign_poe_batch(hashes, env)

        # Corrupt the middle signature
        sigs[2] = bytes([(b + 1) % 256 for b in sigs[2]])

        results = mock_verify_poe_batch(hashes, sigs, env)

        assert results[0] is True
        assert results[1] is True
        assert results[2] is False  # Corrupted
        assert results[3] is True
        assert results[4] is True

    def test_batch_verify_size_mismatch(self):
        """Verify that batch verify raises error for size mismatch."""
        hashes = [hashlib.sha3_256(f"data{i}".encode()).digest() for i in range(5)]
        sigs = mock_sign_poe_batch(hashes, "dev")

        with pytest.raises(ValueError, match="must have the same length"):
            mock_verify_poe_batch(hashes, sigs[:3], "dev")


class TestMOCKQPCPerformance:
    """Test performance characteristics."""

    def test_sign_performance(self, benchmark):
        """Benchmark sign operation (should be < 1ms)."""
        data_hash = hashlib.sha3_256(b"test_data").digest()
        env = "dev"

        # pytest-benchmark will run this multiple times and report statistics
        result = benchmark(mock_sign_poe, data_hash, env)

        assert len(result) == MOCK_SIGNATURE_SIZE

    def test_verify_performance(self, benchmark):
        """Benchmark verify operation (should be < 1ms)."""
        data_hash = hashlib.sha3_256(b"test_data").digest()
        env = "dev"
        signature = mock_sign_poe(data_hash, env)

        # pytest-benchmark will run this multiple times and report statistics
        result = benchmark(mock_verify_poe, data_hash, signature, env)

        assert result is True


class TestMOCKQPCDeterminismStress:
    """Stress test determinism with many iterations."""

    def test_100_iterations_determinism(self):
        """Verify determinism across 100 iterations."""
        data_hash = hashlib.sha3_256(b"stress_test").digest()
        env = "dev"

        # Sign 100 times
        signatures = [mock_sign_poe(data_hash, env) for _ in range(100)]

        # All must be identical
        assert len(set(signatures)) == 1

    def test_multiple_data_points_determinism(self):
        """Verify determinism for multiple different data points."""
        env = "dev"

        # Create 50 different data hashes
        data_hashes = [
            hashlib.sha3_256(f"data{i}".encode()).digest() for i in range(50)
        ]

        # Sign each one twice
        sigs_round1 = [mock_sign_poe(h, env) for h in data_hashes]
        sigs_round2 = [mock_sign_poe(h, env) for h in data_hashes]

        # Each pair should be identical
        assert sigs_round1 == sigs_round2
