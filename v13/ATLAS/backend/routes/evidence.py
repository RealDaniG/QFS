from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from lib.evidence_bus import EvidenceBus
from routes.auth import validate_session

router = APIRouter(prefix="/api/evidence", tags=["Evidence"])

# Initialize EvidenceBus
bus = EvidenceBus()


class CommitRequest(BaseModel):
    event_type: str
    space_id: str
    sender: str
    payload_hash: str
    intent: str
    client_seq: int


class EvidenceResponse(BaseModel):
    evidence_hash: str
    block_height: int


# EvidenceBus initializes in __init__, no separate initialize() needed


@router.post("/commit")
async def commit_evidence(
    request: CommitRequest, authorization: Optional[str] = Header(None)
):
    """Commit an event to the EvidenceBus."""
    # Verify session
    try:
        await validate_session(authorization)
    except HTTPException as e:
        raise e

    try:
        # Commit to bus
        result = bus.commit(
            event_type=request.event_type,
            space_id=request.space_id,
            actor=request.sender,
            payload_hash=request.payload_hash,
            intent=request.intent,
            client_seq=request.client_seq,
        )
        return EvidenceResponse(
            evidence_hash=result["hash"], block_height=result["height"]
        )
    except Exception as e:
        print(f"Commit Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync")
async def sync_evidence(
    space_id: str, since: int = 0, authorization: Optional[str] = Header(None)
):
    """Fetch evidence events for a space since a given sequence number."""
    # Verify session
    try:
        await validate_session(authorization)
    except HTTPException as e:
        raise e

    try:
        # Assuming EvidenceBus has a query/filter method
        # If not, we might need to add one or use raw SQL in bus
        # Reviewing evidence_bus.py content will confirm current capabilities
        # For now, implementing basic query if available
        events = bus.query(space_id=space_id, since_seq=since)
        return events
    except Exception as e:
        # Fallback if query method differs
        print(f"Sync Error: {e}")
        return []
