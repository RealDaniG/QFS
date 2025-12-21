"""
V1 Auth Compatibility Layer
Thin wrapper around existing auth.py for backward compatibility with legacy scripts.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from . import auth  # Import the main auth module

router = APIRouter(prefix="/api/v1/auth", tags=["auth-v1-compat"])


class NonceRequest(BaseModel):
    wallet_address: str


class NonceResponse(BaseModel):
    nonce: str
    wallet_address: str


class VerifyRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str


class VerifyResponse(BaseModel):
    session_token: str
    wallet_address: str


@router.post("/nonce", response_model=NonceResponse)
async def get_nonce_v1(request: NonceRequest):
    """V1 compatibility: Get nonce for wallet authentication."""
    # Use existing auth challenge logic
    challenge_req = auth.ChallengeRequest(wallet_address=request.wallet_address)
    challenge_data = await auth.create_challenge(challenge_req)

    return NonceResponse(
        nonce=challenge_data["nonce"], wallet_address=request.wallet_address
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_signature_v1(request: VerifyRequest):
    """V1 compatibility: Verify signature and create session."""
    # Use existing auth verify logic
    verify_req = auth.VerifyRequest(
        wallet_address=request.wallet_address,
        signature=request.signature,
        message=request.message,
    )

    session_response = await auth.verify_signature(verify_req)

    return VerifyResponse(
        session_token=session_response.session_token,
        wallet_address=session_response.wallet_address,
    )
