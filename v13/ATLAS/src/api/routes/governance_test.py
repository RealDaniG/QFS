"""
Ultra-minimal governance routes for testing - NO external dependencies
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v18/governance", tags=["governance-v18"])


class ProposalSummary(BaseModel):
    id: str
    title: str
    description: str
    creator: str
    status: str
    votes_for: int
    votes_against: int


@router.get("/proposals", response_model=List[ProposalSummary])
async def list_proposals():
    """Test endpoint - returns mock data"""
    return [
        ProposalSummary(
            id="test001",
            title="Test Proposal",
            description="This is a test",
            creator="0x1234",
            status="active",
            votes_for=10,
            votes_against=2,
        )
    ]


@router.get("/status")
async def status():
    """Simple status check"""
    return {"status": "ok", "service": "governance"}

