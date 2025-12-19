"""
WalletAuth.py - EVM Wallet Signature Verification
"""

from eth_account import Account
from eth_account.messages import encode_defunct


class WalletAuth:
    """
    Handles cryptographic verification of wallet signatures.
    """

    @staticmethod
    def verify_signature(message: str, signature: str, expected_address: str) -> bool:
        """
        Verifies that a message was signed by the private key belonging to expected_address.

        Args:
            message: The raw message string (e.g. the nonce).
            signature: The hex signature string (starting with 0x).
            expected_address: The Ethereum address claiming to sign.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            # EIP-191: Encode as "Ethereum Signed Message"
            msg_hash = encode_defunct(text=message)

            # Recover address from signature
            recovered_address = Account.recover_message(msg_hash, signature=signature)

            # Compare addresses (case-insensitive)
            return recovered_address.lower() == expected_address.lower()
        except Exception as e:
            # Log error in production
            return False
