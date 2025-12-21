from fastapi import APIRouter, Body
from src.lib.storage import db

router = APIRouter(prefix="/api/v18/governance", tags=["governance"])


@router.get("/proposals")
async def get_proposals_v18(status: str = None):
    proposals = db.get_proposals()
    if status:
        return [p for p in proposals if p["status"] == status]
    return proposals


@router.post("/vote")
async def cast_vote_v18(payload: dict = Body(...)):
    # payload: { proposalId, voter, choice }
    # In future use Pydantic VotePayload
    proposal_id = payload.get("proposalId")
    choice = payload.get("choice")

    proposals = db.get_proposals()
    for p in proposals:
        if p["id"] == proposal_id:
            if choice == "yes":
                p["votes_for"] += 1
            elif choice == "no":
                p["votes_against"] += 1
            return {"status": "voted", "proposal": p}

    return {"status": "error", "message": "Proposal not found"}
