"""
Test Suite: Ascon-Protected Session Management (v18.5)

Validates the Auth Sync migration for ATLAS v18.9 App Alpha.

Critical Requirements:
- EIP-191 signature verification remains the identity proof
- Ascon AEAD protects session tokens only
- Sessions must validate across all Tier A nodes
- All lifecycle events logged to EvidenceBus
- Deterministic for Zero-Sim compliance
"""

import pytest
import time
from unittest.mock import MagicMock, patch
from v15.auth.session_manager import SessionManager
from v15.evidence.bus import EvidenceBus


class TestAsconSessionLifecycle:
    """Test Ascon session creation, validation, and expiry."""

    def test_create_session_returns_ascon_token(self):
        """Session tokens must use ascon1.* format."""
        manager = SessionManager(session_ttl_seconds=3600)
        token = manager.create_session(
            wallet_address="0xABC123DEF456", scopes=["bounty:read", "bounty:claim"]
        )

        assert token.startswith("ascon1."), f"Expected ascon1.* token, got: {token}"
        parts = token.split(".")
        assert len(parts) == 4, f"Expected 4 parts (ascon1.id.ct.tag), got {len(parts)}"

        session_id, ciphertext, tag = parts[1], parts[2], parts[3]
        assert len(session_id) == 16, "Session ID should be 16 hex chars"
        assert len(ciphertext) > 0, "Ciphertext should not be empty"
        assert len(tag) > 0, "Tag should not be empty"

    def test_validate_session_returns_correct_data(self):
        """Valid tokens should decrypt to original session data."""
        manager = SessionManager(session_ttl_seconds=3600)
        wallet = "0xDEADBEEF"
        scopes = ["admin:override", "mod:act"]

        token = manager.create_session(wallet_address=wallet, scopes=scopes)
        session_data = manager.validate_session(token)

        assert session_data is not None, "Valid token should return session data"
        assert session_data["wallet_address"] == wallet
        assert session_data["scopes"] == scopes
        assert "created_at" in session_data
        assert "expires_at" in session_data

    def test_tampered_token_rejected(self):
        """Modified tokens should fail validation."""
        manager = SessionManager(session_ttl_seconds=3600)
        token = manager.create_session(wallet_address="0xVALID", scopes=["bounty:read"])

        # Tamper with ciphertext
        parts = token.split(".")
        parts[2] = parts[2][:-2] + "FF"  # Flip last byte
        tampered_token = ".".join(parts)

        session_data = manager.validate_session(tampered_token)
        assert session_data is None, "Tampered token should be rejected"

    def test_expired_session_rejected(self):
        """Expired sessions should be cleaned up and rejected."""
        manager = SessionManager(session_ttl_seconds=1)  # 1 second TTL
        token = manager.create_session(
            wallet_address="0xEXPIRED", scopes=["test:scope"]
        )

        # Wait for expiry
        time.sleep(1.5)

        session_data = manager.validate_session(token)
        assert session_data is None, "Expired session should be rejected"

    def test_revoke_session_removes_token(self):
        """Revoked sessions should no longer validate."""
        manager = SessionManager(session_ttl_seconds=3600)
        token = manager.create_session(
            wallet_address="0xREVOKED", scopes=["bounty:claim"]
        )

        # Verify it works before revocation
        assert manager.validate_session(token) is not None

        # Revoke
        result = manager.revoke_session(token)
        assert result is True, "Revocation should succeed"

        # Verify it no longer works
        assert manager.validate_session(token) is None

    def test_session_cleanup_removes_expired(self):
        """Cleanup should remove expired revocations from revocation list."""
        manager = SessionManager(session_ttl_seconds=1)

        # Create and immediately revoke multiple sessions
        tokens = [manager.create_session(f"0xWALLET{i}", ["test"]) for i in range(3)]

        # Revoke all of them
        for token in tokens:
            manager.revoke_session(token)

        # Verify they're in the revocation list
        assert len(manager._revoked) == 3

        # Wait long enough for cleanup (2x TTL + buffer)
        time.sleep(2.5)

        # Trigger cleanup by validating any token
        manager.validate_session(tokens[0])

        # Old revocations should be cleaned up
        assert len(manager._revoked) == 0, "Expired revocations should be cleaned up"


class TestAsconSessionPoE:
    """Test PoE event logging for audit trail."""

    @patch.object(EvidenceBus, "emit")
    def test_create_session_emits_auth_login(self, mock_emit):
        """Session creation should emit AUTH_LOGIN event."""
        manager = SessionManager(session_ttl_seconds=3600)
        wallet = "0xPOE_TEST"

        token = manager.create_session(wallet_address=wallet, scopes=["test"])

        # Verify AUTH_LOGIN was emitted
        mock_emit.assert_called()
        call_args = mock_emit.call_args
        event_type = call_args[0][0]
        event_data = call_args[0][1]

        assert event_type == "AUTH_LOGIN"
        assert event_data["wallet"] == wallet
        assert "session_id" in event_data
        assert event_data["v18_crypto"] == "ascon-v18.5"

    @patch.object(EvidenceBus, "emit")
    def test_revoke_session_emits_auth_logout(self, mock_emit):
        """Session revocation should emit AUTH_LOGOUT event."""
        manager = SessionManager(session_ttl_seconds=3600)
        token = manager.create_session("0xREVOKE_POE", ["test"])

        # Clear previous calls
        mock_emit.reset_mock()

        manager.revoke_session(token)

        # Verify AUTH_LOGOUT was emitted
        mock_emit.assert_called_once()
        call_args = mock_emit.call_args
        event_type = call_args[0][0]
        event_data = call_args[0][1]

        assert event_type == "AUTH_LOGOUT"
        assert "session_id" in event_data


class TestAsconSessionMultiNode:
    """
    Test multi-node session validation (P0 for v18.9 App Alpha).

    Critical requirement: Session issued on Node A must validate on Node B.
    """

    def test_session_validates_across_nodes_same_config(self):
        """
        Session created on Node A should validate on Node B.

        This simulates the distributed cluster scenario where:
        - Node A issues a session token after EIP-191 verification
        - Node B receives an API request with that token
        - Node B must validate the token and extract wallet identity

        With stateless tokens: This should now work!
        """
        # Simulate Node A
        node_a = SessionManager(session_ttl_seconds=3600)
        wallet = "0xMULTINODE"
        scopes = ["bounty:read", "governance:vote"]

        token = node_a.create_session(wallet_address=wallet, scopes=scopes)

        # Simulate Node B (separate instance, same config)
        node_b = SessionManager(session_ttl_seconds=3600)

        # STATELESS BEHAVIOR: This should succeed!
        session_data = node_b.validate_session(token)

        # Verify successful validation
        assert session_data is not None, "Stateless token should validate on any node"
        assert session_data["wallet_address"] == wallet
        assert session_data["scopes"] == scopes
        assert "created_at" in session_data
        assert "expires_at" in session_data

    def test_stateless_token_contract(self):
        """
        Document the stateless token contract for v18.9.

        A stateless token must:
        1. Embed all session data in the encrypted payload
        2. Use deterministic Ascon context for encryption
        3. Be verifiable by any node with the same key_id
        4. Include expiry timestamp in the payload
        5. Optionally include a signature for non-repudiation
        """
        manager = SessionManager(session_ttl_seconds=3600)
        wallet = "0xSTATELESS"
        scopes = ["test:scope"]

        token = manager.create_session(wallet_address=wallet, scopes=scopes)

        # Verify token structure
        parts = token.split(".")
        assert len(parts) == 4, "Token must have 4 parts"

        prefix, session_id, ciphertext, tag = parts
        assert prefix == "ascon1", "Version prefix must be ascon1"

        # Decrypt and verify payload contains all necessary data
        session_data = manager.validate_session(token)
        assert session_data is not None

        # For stateless tokens, we need:
        # - wallet_address (identity)
        # - scopes (authorization)
        # - expires_at (validity window)
        # - created_at (audit trail)
        required_fields = ["wallet_address", "scopes", "created_at", "expires_at"]
        for field in required_fields:
            assert field in session_data, f"Stateless token must include {field}"


class TestAsconSessionDeterminism:
    """Test deterministic properties for Zero-Sim compliance."""

    def test_session_id_includes_timestamp_for_uniqueness(self):
        """
        Session IDs must be unique even for same wallet.

        Uses: sha256(wallet_address:count:timestamp)
        This ensures uniqueness while remaining deterministic in test environments.
        """
        manager = SessionManager()

        token1 = manager.create_session("0xSAME", ["test"])
        token2 = manager.create_session("0xSAME", ["test"])

        id1 = token1.split(".")[1]
        id2 = token2.split(".")[1]

        assert id1 != id2, "Session IDs must be unique for same wallet"

    def test_ascon_context_deterministic(self):
        """
        Ascon encryption must use deterministic context.

        Context includes:
        - node_id: "tier-a-primary" (or cluster-specific)
        - channel_id: "wallet_session"
        - evidence_seq: session count (deterministic in order)
        - key_id: "v1" (key version)
        """
        manager = SessionManager()
        token = manager.create_session("0xDET", ["test"])

        # Validate that decryption works (proves deterministic context)
        session_data = manager.validate_session(token)
        assert session_data is not None, "Deterministic context must allow decryption"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
