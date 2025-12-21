"""
V1 Auth Compatibility Layer for src/api/routes
Thin wrapper around existing auth.py for backward compatibility with legacy scripts.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from . import auth as auth_mod  # Import the main auth module

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
@router.get("/nonce", response_model=NonceResponse)
async def get_nonce_v1(
    wallet_address: Optional[str] = None, request: Optional[NonceRequest] = None
):
    """V1 compatibility: Get nonce for wallet authentication."""
    # Support both POST with body and GET with query params
    addr = wallet_address
    if not addr and request:
        addr = request.wallet_address

    if not addr:
        # For legacy compatibility scripts that might omit the address to just get A nonce
        addr = "0x0000000000000000000000000000000000000000"

    # In src/api/routes/auth.py, get_nonce_v18 generates a nonce.
    data = await auth_mod.get_nonce_v18()
    return NonceResponse(nonce=data["nonce"], wallet_address=addr)


@router.post("/verify", response_model=VerifyResponse)
@router.post(
    "/login", response_model=VerifyResponse
)  # Added /login alias for verify_auth.py
async def verify_signature_v1(request: VerifyRequest):
    """V1 compatibility: Verify signature and create session."""
    # Use existing auth verify logic
    verify_req = auth_mod.VerifyRequest(
        wallet_address=request.wallet_address,
        signature=request.signature,
        message=request.message,
    )

    session_response = await auth_mod.verify_signature(verify_req)

    return VerifyResponse(
        session_token=session_response.session_token,
        wallet_address=session_response.wallet_address,
    )
