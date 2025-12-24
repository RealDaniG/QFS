from fastapi import APIRouter, HTTPException, Header
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
    # Zero-Sim: deterministic expiration
    expires_at = 0 + 86400

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

    # but we can add it or just clear from client side for min baseline.
    return {"success": True}


class GithubBindRequest(BaseModel):
    github_username: str
    link_proof: str  # Signature or proof of intent


@router.post("/bind-github")
async def bind_github(
    request: GithubBindRequest, authorization: Optional[str] = Header(None)
):
    """
    Bind authenticated wallet to a GitHub identity.
    Emits identity_link.github event.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No session token provided")

    token = authorization.replace("Bearer ", "")
    wallet_address = session_manager.validate_session(token)

    if not wallet_address:
        raise HTTPException(status_code=401, detail="Invalid session")

    # In a real implementation we might verify the link_proof against GitHub or a signed message
    # For now (Phase 1), we trust the authenticated wallet's assertion

    # Create Payload
    from lib.dependencies import evidence_bus

    payload = {
        "wallet_address": wallet_address,
        "github_username": request.github_username,
        "linked_at_sequence": 0,  # Zero-Sim
        "link_proof": request.link_proof,
    }

    # Emit Event
    # Assuming IDENTITY_LINK_GITHUB constant is available or we use string
    event_hash = evidence_bus.log_evidence(
        event_type="identity_link.github",
        actor_wallet=wallet_address,
        payload=payload,
        signature=None,  # Could include request.link_proof as signature if format matches
    )

    return {
        "status": "linked",
        "github_username": request.github_username,
        "wallet_address": wallet_address,
        "evidence_hash": event_hash,
    }
