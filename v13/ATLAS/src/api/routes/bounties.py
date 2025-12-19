"""
Bounties API Routes
Protected routes for bounty management.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ..dependencies import get_current_session

router = APIRouter(prefix="/bounties", tags=["bounties"])

# Mock Data (Phase 3)
BOUNTIES = [
    {
        "id": "BNT-001",
        "title": "Implement Wallet Login",
        "reward": 500,
        "status": "OPEN",
        "claimant": None,
    },
    {
        "id": "BNT-002",
        "title": "Fix QFS Replay Bug",
        "reward": 1200,
        "status": "CLAIMED",
        "claimant": "0x123...abc",
    },
]


class Bounty(BaseModel):
    id: str
    title: str
    reward: int
    status: str
    claimant: Optional[str]


@router.get("/", response_model=List[Bounty])
async def list_bounties(session: dict = Depends(get_current_session)):
    """
    List all bounties.
    Requires: Valid Session (Scope: bounty:read)
    """
    # Scope check
    if "bounty:read" not in session.get("scopes", []):
        raise HTTPException(status_code=403, detail="Missing scope: bounty:read")

    return BOUNTIES


@router.post("/{bounty_id}/claim")
async def claim_bounty(bounty_id: str, session: dict = Depends(get_current_session)):
    """
    Claim a bounty for the current wallet.
    Requires: Valid Session (Scope: bounty:claim)
    """
    if "bounty:claim" not in session.get("scopes", []):
        raise HTTPException(status_code=403, detail="Missing scope: bounty:claim")

    # In Phase 3, we mock the logic
    # In Phase 4/5, this will write to DB/Queue

    return {
        "status": "success",
        "message": f"Bounty {bounty_id} claimed by {session['wallet_address']}",
        "bounty_id": bounty_id,
    }


@router.get("/my-bounties")
async def my_bounties(session: dict = Depends(get_current_session)):
    """
    List bounties claimed by the authenticated user.
    """
    # Mock filtering
    return [b for b in BOUNTIES if b["claimant"] == session["wallet_address"]]
