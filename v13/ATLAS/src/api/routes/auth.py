"""
Auth API Routes
Handles wallet authentication via challenge-response.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from v15.atlas.auth.nonce_manager import NonceManager
from v15.atlas.auth.wallet_auth import WalletAuth
from v15.atlas.auth.session_manager import SessionManager

router = APIRouter(prefix="/auth", tags=["auth"])

# Instantiate Managers (Singleton for now)
# In production, these should be initialized at app startup or via dependency injection
nonce_manager = NonceManager()
session_manager = SessionManager()


class LoginRequest(BaseModel):
    nonce: str
    signature: str
    wallet_address: str


class LoginResponse(BaseModel):
    session_token: str
    wallet_address: str
    expires_at: float


@router.get("/nonce")
async def get_nonce():
    """Generates a new ephemeral nonce for the client to sign."""
    nonce = nonce_manager.generate_nonce()
    return {"nonce": nonce}


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Verifies the wallet signature and issues a session token.
    """
    # 1. Validate Nonce (exists and not expired)
    # Note: validate_nonce consumes it, so we must be careful with retries.
    # But for security, verify_signature needs the original message (nonce).
    # We check if it WAS valid.
    # Actually, WalletAuth needs the nonce as the message.
    # NonceManager.validate_nonce checks if it exists in store.

    # We first verify the signature logic.
    # But wait, we need to know if the nonce passed is actually one WE issued.
    # So we must check validity first.

    if not nonce_manager.validate_nonce(request.nonce):
        raise HTTPException(status_code=400, detail="Invalid or expired nonce")

    # 2. Verify Signature
    is_valid = WalletAuth.verify_signature(
        message=request.nonce,
        signature=request.signature,
        expected_address=request.wallet_address,
    )

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 3. Create Session
    # Default scopes for now
    scopes = ["bounty:read", "bounty:claim"]
    token = session_manager.create_session(request.wallet_address, scopes=scopes)
    session_data = session_manager.validate_session(token)

    if not session_data:
        raise HTTPException(status_code=500, detail="Failed to create session")

    return {
        "session_token": token,
        "wallet_address": session_data["wallet_address"],
        "expires_at": session_data["expires_at"],
    }


@router.post("/logout")
async def logout(session_token: str = Body(..., embed=True)):
    """Revokes the current session."""
    session_manager.revoke_session(session_token)
    return {"status": "success"}
