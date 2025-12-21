"""
V1 Auth Compatibility Layer
Thin wrapper around existing auth.py for backward compatibility with legacy scripts.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from lib.dependencies import session_manager

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
    message, nonce = session_manager.create_challenge(request.wallet_address)
    return NonceResponse(nonce=nonce, wallet_address=request.wallet_address)


@router.post("/verify", response_model=VerifyResponse)
async def verify_signature_v1(request: VerifyRequest):
    """V1 compatibility: Verify signature and create session."""
    is_valid = session_manager.verify_signature(
        request.wallet_address, request.message, request.signature
    )

    if not is_valid:
        raise HTTPException(status_code=401, detail="Signature verification failed")

    session_token = session_manager.create_session_token(
        request.wallet_address, request.signature
    )

    return VerifyResponse(
        session_token=session_token,
        wallet_address=request.wallet_address,
    )
