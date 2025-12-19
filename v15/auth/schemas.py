"""
Auth Schemas (v16 Baseline)
"""

from typing import Optional
from pydantic import BaseModel, Field


class WalletConnectRequest(BaseModel):
    """
    Validation schema for Wallet Connect requests.
    Corresponds to EIP-191 signature over a nonce/message.
    """

    wallet_address: str = Field(..., description="0x address of the user wallet")
    message: str = Field(..., description="The raw message that was signed")
    signature: str = Field(..., description="Hex string of the signature")
    nonce: str = Field(..., description="Unique nonce to prevent replay")


class SessionCreate(BaseModel):
    """
    Internal session creation payload after verification.
    """

    user_id: str
    scopes: list[str] = []


class AuthEvent(BaseModel):
    """
    Event emitted to EvidenceBus
    """

    event_type: str = "AUTH_LOGIN"
    wallet_address: str
    success: bool
    signature_hash: str
