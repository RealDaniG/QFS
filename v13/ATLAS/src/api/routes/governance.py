from fastapi import APIRouter, Body, HTTPException, Depends
import json
from typing import List, Optional, Dict, Any
from v13.atlas.src.api.dependencies import get_evidence_bus
from v17.ui.governance_projection import GovernanceProjection
from v17.governance.schemas import GovernanceConfig

router = APIRouter(prefix="/api/v18/governance", tags=["governance"])

# Initialize Projection (V17)
# In production, this would be a singleton service


class EvidenceBusAdapter:
    """Adapts V13 EvidenceBus to V17 GovernanceProjection interface."""

    def __init__(self, v13_bus):
        self.bus = v13_bus

    def get_events(self, limit: int = 50) -> List[Dict]:
        rows = self.bus.get_recent_evidence(limit=limit)
        events = []
        for row in rows:
            # Parse payload from JSON string
            try:
                payload = json.loads(row["payload"])
            except:
                payload = {}

            # Map to V17 envelope structure
            events.append(
                {
                    "event": {
                        "type": row["event_type"],
                        "payload": payload,
                        "timestamp": row["timestamp"],
                    }
                }
            )
        return events


def get_projection(bus=Depends(get_evidence_bus)):
    adapter = EvidenceBusAdapter(bus)
    return GovernanceProjection(adapter)


@router.get("/proposals")
async def get_proposals_v18(
    status: str = None, proj: GovernanceProjection = Depends(get_projection)
):
    # V17 Projection returns list of dicts
    proposals = proj.list_proposals(limit=100)
    if status:
        return [p for p in proposals if p["status"] == status]
    return proposals


@router.post("/vote")
async def cast_vote_v18(payload: dict = Body(...), bus=Depends(get_evidence_bus)):
    # Emulate V17 flow: Emit event -> Projection updates
    proposal_id = payload.get("proposalId")
    choice = payload.get("choice")
    voter = payload.get("voter", "0x0000")  # Should come from auth

    if not proposal_id or not choice:
        raise HTTPException(status_code=400, detail="Missing proposalId or choice")

    # Emit Vote Event (V17 schema compliant)
    bus.emit(
        "GOV_VOTE_CAST",
        {
            "vote": {
                "proposal_id": proposal_id,
                "choice": choice,
                "weight": "1.000000000000000000",  # Mock weight for staging
                "voter_wallet": voter,
                "timestamp": 0,  # Zero-Sim
            }
        },
    )

    return {"status": "voted", "proposal_id": proposal_id}
