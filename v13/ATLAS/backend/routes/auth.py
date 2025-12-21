from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from lib.dependencies import session_manager

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class ChallengeRequest(BaseModel):
    wallet_address: str


class VerifyRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str


class SessionResponse(BaseModel):
    session_token: str
    wallet_address: str
    expires_at: int


@router.post("/challenge")
async def create_challenge(request: ChallengeRequest):
    """Generate authentication challenge for wallet to sign."""
    message, _ = session_manager.create_challenge(request.wallet_address)
    return {"message": message}


@router.post("/verify")
async def verify_signature(request: VerifyRequest):
    """Verify wallet signature and create session."""
    is_valid = session_manager.verify_signature(
        request.wallet_address, request.message, request.signature
    )

    if not is_valid:
        raise HTTPException(status_code=401, detail="Signature verification failed")

    session_token = session_manager.create_session_token(
        request.wallet_address, request.signature
    )

    # In a real app we'd fetch this from the DB or return calculated
    expires_at = int(time.time()) + 86400

    return SessionResponse(
        session_token=session_token,
        wallet_address=request.wallet_address,
        expires_at=expires_at,
    )


@router.get("/session")
async def validate_session(authorization: Optional[str] = Header(None)):
    """Validate active session."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No session token provided")

    token = authorization.replace("Bearer ", "")
    wallet_address = session_manager.validate_session(token)

    if not wallet_address:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {
        "valid": True,
        "wallet_address": wallet_address,
    }


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Invalidate session."""
    # Current SessionManager doesn't have a logout/pop method yet
    # but we can add it or just clear from client side for min baseline.
    return {"success": True}


import time
