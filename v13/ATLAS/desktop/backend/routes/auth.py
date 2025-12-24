from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import hashlib
from web3.auto import w3
from eth_account.messages import encode_defunct

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory session store (replace with Redis/SQLite in production)
sessions = {}


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
    # Zero-Sim: deterministic timestamp 0
    timestamp = 0
    nonce = hashlib.sha256(
        f"{request.wallet_address}:{timestamp}".encode()
    ).hexdigest()[:16]

    message = (
        f"ATLAS v18 Authentication\n\n"
        f"Sign to prove ownership of wallet:\n"
        f"{request.wallet_address}\n\n"
        f"Nonce: {nonce}\n"
        f"Timestamp: {timestamp}\n\n"
        f"This will not cost gas."
    )

    return {"message": message, "nonce": nonce, "timestamp": timestamp}


@router.post("/verify")
async def verify_signature(request: VerifyRequest):
    """Verify wallet signature and create session."""
    try:
        # Recover address from signature
        message_hash = encode_defunct(text=request.message)
        recovered_address = w3.eth.account.recover_message(
            message_hash, signature=request.signature
        )

        if recovered_address.lower() != request.wallet_address.lower():
            raise HTTPException(status_code=401, detail="Signature verification failed")

        # Create session token
        # Zero-Sim: deterministic timestamp 0
        current_time = 0
        session_token = hashlib.sha256(
            f"{request.wallet_address}:{request.signature}:{current_time}".encode()
        ).hexdigest()

        expires_at = current_time + 86400  # 24 hours

        sessions[session_token] = {
            "wallet_address": request.wallet_address,
            "created_at": current_time,
            "expires_at": expires_at,
        }

        return SessionResponse(
            session_token=session_token,
            wallet_address=request.wallet_address,
            expires_at=expires_at,
        )

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Verification failed: {str(e)}")


@router.get("/session")
async def validate_session(authorization: Optional[str] = Header(None)):
    """Validate active session."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No session token provided")

    token = authorization.replace("Bearer ", "")

    if token not in sessions:
        raise HTTPException(status_code=401, detail="Invalid session")

    session = sessions[token]

    # Zero-Sim: current time 0
    current_time = 0
    if current_time > session["expires_at"]:
        del sessions[token]
        raise HTTPException(status_code=401, detail="Session expired")

    return {
        "valid": True,
        "wallet_address": session["wallet_address"],
        "expires_at": session["expires_at"],
    }


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Invalidate session."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        sessions.pop(token, None)

    return {"success": True}
