from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from src.lib.dependencies import evidence_bus, session_manager
from v13.qfs.events.contributions import CONTRIB_RECORDED

router = APIRouter(prefix="/api/bounties", tags=["Bounties"])


class ContributionEntry(BaseModel):
    contribution_id: str
    github_username: str
    pr_number: int
    lines_added: int
    lines_deleted: int
    files_changed: List[str]
    component_tag: str
    weight_inputs: Dict[str, Any]


class ImportContribRequest(BaseModel):
    round_id: str
    importer_version: str
    repo: str
    contributions: List[ContributionEntry]
    ledger_hash: str


@router.get("/my-rewards")
async def get_my_rewards(authorization: Optional[str] = Header(None)):
    """
    Get retroactive rewards for the authenticated wallet.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No session token provided")

    token = authorization.replace("Bearer ", "")
    # session_manager is imported at module level from src.lib.dependencies

    wallet_address = session_manager.validate_session(token)
    if not wallet_address:
        raise HTTPException(status_code=401, detail="Invalid session")

    from v13.qfs.f_layer.bounty_github import get_rewards_from_events

    rewards = get_rewards_from_events(evidence_bus, wallet_address)

    return {
        "wallet_address": wallet_address,
        "total_rewards": sum(r["amount"] for r in rewards),
        "history": rewards,
    }


@router.post("/import-contrib")
async def import_contributions(
    request: ImportContribRequest, authorization: Optional[str] = Header(None)
):
    """
    Ingest a deterministic contribution ledger.
    Emits contrib_recorded events for mapped identities.
    """
    # Phase 2: Open ingestion for dev/test (or restrict to admin in production)
    # For now, we allow anyone to post a ledger for testing retro simulation

    events_emitted = []

    for contrib in request.contributions:
        # Resolve Identity (Mock/Simple Lookup for now)
        # In real Phase 2, we should query evidence_bus for identity_link.github
        # Here we trust the flow or lookup if possible, or just emit with username
        # To make it strict: we query 'identity_link.github' from evidence bus

        # NOTE: EvidenceBus is append-only log, querying state requires projection
        # For this MVC, we will emit the event containing the github_username
        # The F-Layer (reward engine) will do the join.

        payload = {
            "round_id": request.round_id,
            "contribution_id": contrib.contribution_id,
            "github_username": contrib.github_username,
            "repo": request.repo,
            "score_inputs": {
                "lines_added": contrib.lines_added,
                "lines_deleted": contrib.lines_deleted,
                "files": len(contrib.files_changed),
            },
            "importer_version": request.importer_version,
            "original_ledger_hash": request.ledger_hash,
        }

        event_hash = evidence_bus.log_evidence(
            event_type=CONTRIB_RECORDED,
            actor_wallet="0x0000000000000000000000000000000000000000",  # System/Ingester
            payload=payload,
        )
        events_emitted.append(event_hash)

    return {
        "status": "ingested",
        "count": len(events_emitted),
        "events": events_emitted,
    }
