"""
QFS v20 Auth Service
FastAPI microservice for authentication operations.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

from v15.auth.session import Session
from v15.auth.session_id import SessionIDGenerator
from v15.auth.device import compute_device_hash, get_device_info
from v15.auth.events import create_session_created_event
from v15.services.session_store import SessionStore
from v15.services.evidence_adapter import EvidenceBusAdapter
from v15.api.time_provider import get_logical_time
from v15.api.github_oauth import router as github_router

app = FastAPI(title="QFS Auth Service", version="20.0.0-alpha")

# Include GitHub OAuth Router
app.include_router(github_router)

# Initialize components
# TODO: Get node_seed from secure config for production
session_id_gen = SessionIDGenerator(node_seed="dev_node_001")
session_store = SessionStore()
evidence_adapter = EvidenceBusAdapter()


class LoginRequest(BaseModel):
    """Payload for wallet-based login."""

    wallet_address: str
    signature: str
    nonce: str


class SessionResponse(BaseModel):
    session_id: str
    expires_at: int
    device_id: str


@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth", "version": "20.0.0-alpha"}


@app.post("/auth/session", response_model=SessionResponse)
async def create_session(
    req: LoginRequest, logical_time: int = Depends(get_logical_time)
) -> SessionResponse:
    """
    Create new auth session (wallet login).

    Steps:
    1. Verify wallet signature (TODO: implement verification)
    2. Generate deterministic session ID
    3. Compute device hash
    4. Create session
    5. Emit SESSION_CREATED event
    6. Store session
    """

    # TODO: Verify signature
    # For now, accept all (dev mode)

    # Generate session ID
    issued_at = logical_time
    session_id = session_id_gen.generate(req.wallet_address, issued_at)

    # Compute device hash
    os_family, cpu_arch, app_uuid = get_device_info()
    device_hash = compute_device_hash(os_family, cpu_arch, app_uuid)

    # Create session
    session = Session(
        session_id=session_id,
        subject_ids={"wallet": req.wallet_address},
        device_id=device_hash,
        roles=["user"],
        scopes=["read", "write"],
        issued_at=issued_at,
        expires_at=issued_at + 3600,  # 1 hour
        refresh_index=0,
    )

    # Emit event
    event = create_session_created_event(
        session_id=session_id,
        wallet_address=req.wallet_address,
        device_hash=device_hash,
        issued_at=issued_at,
        expires_at=session.expires_at,
        timestamp=logical_time,
    )
    evidence_adapter.emit(event)

    # Store session
    session_store.save(session)

    return SessionResponse(
        session_id=session.session_id,
        expires_at=session.expires_at,
        device_id=session.device_id,
    )


@app.get("/auth/session/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """Get session by ID."""
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@app.get("/bounty/rewards")
async def get_my_rewards(
    session_id: str, logical_time: int = Depends(get_logical_time)
) -> Dict[str, Any]:
    """
    Get retro rewards for a session.
    In a real implementation, this would query the F-Layer state or EvidenceBus index.
    For Phase 2 Alpha, we return mock data or calculate on the fly from a mock ledger.
    """
    # Mock data for demonstration
    return {
        "round_id": "v20-retro-epoch-1",
        "rewards": [
            {
                "reason": "GitHub PR #123 (Merged)",
                "amount": 5.0,
                "token": "FLX",
                "timestamp": logical_time,
            }
        ],
        "total_flx": 5.0,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
