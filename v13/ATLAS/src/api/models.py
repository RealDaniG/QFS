from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict

# --- Auth Models ---


class VerifyPayload(BaseModel):
    wallet: str = Field(..., alias="wallet_address")
    signature: str
    nonce: Optional[str] = None
    challenge_id: Optional[str] = None


class SessionResponse(BaseModel):
    session_token: str
    expires_at: str
    wallet_address: str
    scopes: List[str]


# --- Governance Models ---


class VotePayload(BaseModel):
    proposalId: str
    choice: Literal["yes", "no"]


# --- Chat Models ---


class SendMessagePayload(BaseModel):
    text: str
    conversation_id: Optional[str] = "conv_1"


# --- Space Models ---
# (Adding specific join payload if needed in future, currently typically just URL param)
