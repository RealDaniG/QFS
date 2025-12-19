"""
test_auth_flow.py - Tests for the v15.4 Wallet Authentication Flow.
"""

import pytest
from eth_account import Account
from eth_account.messages import encode_defunct
from v15.atlas.auth.nonce_manager import NonceManager
from v15.atlas.auth.wallet_auth import WalletAuth
from v15.atlas.auth.session_manager import SessionManager
import uuid


def test_full_auth_flow():
    """
    Tests the complete flow:
    1. Generate nonce.
    2. Sign nonce.
    3. Verify signature.
    4. Create session.
    """

    # Setup Managers
    nonce_mgr = NonceManager()
    session_mgr = SessionManager()

    # 1. Generate Nonce
    nonce = nonce_mgr.generate_nonce()
    assert nonce.startswith("Sign this message")
    assert nonce_mgr.validate_nonce(nonce) is True
    # Nonce should be consumed
    assert nonce_mgr.validate_nonce(nonce) is False

    # Regenerate for signing since validation consumes it
    nonce = nonce_mgr.generate_nonce()

    # 2. Setup Dummy Wallet
    # Use a random private key for testing
    acct = Account.create()
    wallet_address = acct.address
    private_key = acct.key

    # 3. Sign Message
    # Standard EIP-191 signing
    msg_hash = encode_defunct(text=nonce)
    signed_message = acct.sign_message(msg_hash)
    signature = signed_message.signature.hex()

    # 4. Verify Signature
    is_valid = WalletAuth.verify_signature(nonce, signature, wallet_address)
    assert is_valid is True

    # Test Invalid Signature
    is_invalid = WalletAuth.verify_signature("Wrong Nonce", signature, wallet_address)
    assert is_invalid is False

    # Test Wrong Address
    other_acct = Account.create()
    is_invalid = WalletAuth.verify_signature(nonce, signature, other_acct.address)
    assert is_invalid is False

    # 5. Create Session
    token = session_mgr.create_session(
        wallet_address, scopes=["bounty:read", "bounty:claim"]
    )
    assert token.startswith("sess_")

    # 6. Validate Session
    session_data = session_mgr.validate_session(token)
    assert session_data is not None
    assert session_data["wallet_address"] == wallet_address
    assert "bounty:claim" in session_data["scopes"]

    # 7. Revoke Session
    session_mgr.revoke_session(token)
    assert session_mgr.validate_session(token) is None


if __name__ == "__main__":
    test_full_auth_flow()
    print("✅ Auth Flow Tests Passed")
