"""
V18 Governance API Routes
Integrated with ClusterAdapter for distributed writes.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ..dependencies import session_manager, get_current_wallet
from v18.cluster import V18ClusterAdapter, GovernanceCommand, TxResult

router = APIRouter(prefix="/api/v18/governance", tags=["governance-v18"])

# Initialize ClusterAdapter (in production, inject via dependencies)
# For now, use localhost cluster
cluster_adapter = V18ClusterAdapter(
    node_endpoints=[
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
    ],
    timeout_seconds=10,
)


# ============================================================================
# Request/Response Models
# ============================================================================


class CreateProposalRequest(BaseModel):
    title: str
    description: str
    proposal_type: str = "general"
    voting_period_days: int = 7


class CreateProposalResponse(BaseModel):
    proposal_id: str
    committed: bool
    evidence_event_ids: List[str]
    leader_term: int
    leader_node_id: str
    commit_index: int


class CastVoteRequest(BaseModel):
    proposal_id: str
    support: bool  # True = vote for, False = vote against
    comment: Optional[str] = None


class CastVoteResponse(BaseModel):
    vote_id: str
    committed: bool
    evidence_event_ids: List[str]


class ProposalSummary(BaseModel):
    id: str
    title: str
    description: str
    creator: str
    status: str
    votes_for: int
    votes_against: int
    created_at: float


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/proposals", response_model=CreateProposalResponse)
async def create_proposal(
    request: CreateProposalRequest, wallet: str = Depends(get_current_wallet)
):
    """
    Create a new governance proposal.
    Submits via ClusterAdapter to distributed backend.
    """
    try:
        # Create governance command
        cmd = GovernanceCommand(
            action_type="create_proposal",
            wallet_address=wallet,
            proposal_data={
                "title": request.title,
                "description": request.description,
                "proposal_type": request.proposal_type,
                "voting_period_days": request.voting_period_days,
            },
        )

        # Submit to cluster
        result: TxResult = cluster_adapter.submit_governance_action(cmd)

        if not result.committed:
            raise HTTPException(
                status_code=500,
                detail=f"Proposal creation failed: {result.error_message}",
            )

        # Extract proposal ID from first event
        proposal_id = (
            result.evidence_event_ids[0] if result.evidence_event_ids else "unknown"
        )

        return CreateProposalResponse(
            proposal_id=proposal_id,
            committed=result.committed,
            evidence_event_ids=result.evidence_event_ids,
            leader_term=result.leader_term,
            leader_node_id=result.leader_node_id,
            commit_index=result.commit_index,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/proposals/{proposal_id}/vote", response_model=CastVoteResponse)
async def cast_vote(
    proposal_id: str,
    request: CastVoteRequest,
    wallet: str = Depends(get_current_wallet),
):
    """
    Cast a vote on a proposal.
    Submits via ClusterAdapter to distributed backend.
    """
    try:
        cmd = GovernanceCommand(
            action_type="cast_vote",
            wallet_address=wallet,
            proposal_id=proposal_id,
            vote_value="for" if request.support else "against",
        )

        result: TxResult = cluster_adapter.submit_governance_action(cmd)

        if not result.committed:
            raise HTTPException(
                status_code=500, detail=f"Vote failed: {result.error_message}"
            )

        vote_id = (
            result.evidence_event_ids[0] if result.evidence_event_ids else "unknown"
        )

        return CastVoteResponse(
            vote_id=vote_id,
            committed=result.committed,
            evidence_event_ids=result.evidence_event_ids,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals", response_model=List[ProposalSummary])
async def list_proposals(
    status: Optional[str] = None, limit: int = 20, offset: int = 0
):
    """
    List governance proposals.
    Queries from projections/ledger state.
    """
    # TODO: Query from projection database or EvidenceBus
    # For now, return mock data
    return [
        ProposalSummary(
            id="prop_001",
            title="Increase Treasury Allocation",
            description="Proposal to increase FLX allocation for bounties",
            creator="0xABC123",
            status="active",
            votes_for=45,
            votes_against=12,
            created_at=1703001234.5,
        )
    ]


@router.get("/proposals/{proposal_id}", response_model=ProposalSummary)
async def get_proposal(proposal_id: str):
    """
    Get details of a specific proposal.
    """
    # TODO: Query from projection database
    return ProposalSummary(
        id=proposal_id,
        title="Sample Proposal",
        description="This is a sample proposal",
        creator="0xABC123",
        status="active",
        votes_for=10,
        votes_against=2,
        created_at=1703001234.5,
    )


@router.get("/cluster/status")
async def cluster_status():
    """
    Get current cluster health and leader information.
    """
    try:
        status = cluster_adapter.get_cluster_status()
        return {
            "leader_node_id": status.leader_node_id,
            "leader_endpoint": status.leader_endpoint,
            "current_term": status.current_term,
            "commit_index": status.commit_index,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cluster unavailable: {str(e)}")

