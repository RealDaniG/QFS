"""
WalletConnect Adapter (v16 Baseline)

Handles EIP-191 signature verification and Session creation.
Integrates with MOCKQPC-first architecture.
"""

from typing import Optional
from v15.auth.schemas import WalletConnectRequest
from v15.auth.session_manager import SessionManager

# In a real impl, we would import eth_account
# from eth_account.messages import encode_defunct


class WalletAuthService:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def authenticate(self, request: WalletConnectRequest) -> Optional[str]:
        """
        Authenticate a wallet using EIP-191 signature.
        Returns session token if successful, None otherwise.
        """

        # 1. Verify Signature
        if not self._verify_signature(
            request.wallet_address, request.message, request.signature
        ):
            return None

        # 2. Check Nonce (Stateful)
        # TODO: Implement Nonce nonce checking to prevent replay

        # 3. Create Session
        token = self.session_manager.create_session(
            wallet_address=request.wallet_address, scopes=["user:basic"]
        )

        return token

    def _verify_signature(self, address: str, message: str, signature: str) -> bool:
        """
        Verify EIP-191 signature.
        In MOCKQPC/Dev mode, this perform a mock verification.
        """
        # MOCKQPC Logic:
        # If signature == "mock_sig_valid", pass.
        # Or more complex deterministic check.

        if signature == "mock_sig_valid":
            return True

        # In integration, we would do:
        # msg = encode_defunct(text=message)
        # recovered = w3.eth.account.recover_message(msg, signature=signature)
        # return recovered.lower() == address.lower()

        return False
