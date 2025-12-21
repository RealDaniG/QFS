from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from src.api.dependencies import evidence_bus, require_auth

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.post("/commit")
async def commit_evidence(payload: Dict, session: dict = Depends(require_auth)):
    """
    Commit a new evidence event to the append-only log.
    """
    event_type = payload.get("type", "generic_event")
    actor_wallet = session.get("wallet", "unknown")
    event_data = payload.get("payload", {})
    signature = payload.get("signature")
    parent_hash = payload.get("parent_hash")

    evidence_hash = evidence_bus.log_evidence(
        event_type=event_type,
        actor_wallet=actor_wallet,
        payload=event_data,
        signature=signature,
        parent_hash=parent_hash,
    )

    return {"id": evidence_hash, "head_hash": evidence_hash, "status": "committed"}


@router.get("/head")
async def get_evidence_head():
    """
    Return the latest head hash from the EvidenceBus.
    """
    recent = evidence_bus.get_recent_evidence(limit=1)
    if not recent:
        return {"head_hash": "0x" + "0" * 64, "height": 0}

    return {
        "head_hash": recent[0]["evidence_hash"],
        "height": len(recent),  # Simplified for v14v2
    }


@router.get("/recent")
async def get_recent_evidence(limit: int = 50):
    """
    Retrieve the last N evidence events.
    """
    return evidence_bus.get_recent_evidence(limit=limit)
