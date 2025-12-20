"""
Bounty Schemas (v17 Beta)

Pydantic models for deterministic bounty and reward operations.
All state transitions are pure functions consuming EvidenceBus history.
"""

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class Bounty(BaseModel):
    """Deterministic bounty model."""

    bounty_id: str = Field(..., description="Deterministic bounty ID")
    space_id: str = Field(..., description="Space where bounty was created")

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=10000)

    reward_amount: float = Field(..., gt=0.0, description="Total reward amount")
    currency: str = Field(default="QFS", description="Reward currency")

    created_by: str = Field(..., description="Creator wallet address")
    created_at: int = Field(..., description="Deterministic timestamp")
    deadline: Optional[int] = Field(None, description="Optional deadline timestamp")

    tags: List[str] = Field(default_factory=list, description="Bounty tags/categories")
    metadata: Optional[Dict] = Field(default=None, description="Additional bounty data")

    class Config:
        json_schema_extra = {
            "example": {
                "bounty_id": "bounty_space123_1703001234",
                "space_id": "space_123",
                "title": "Implement feature X",
                "description": "We need feature X implemented...",
                "reward_amount": 1000.0,
                "currency": "QFS",
                "created_by": "0xabc...",
                "created_at": 1703001234,
                "deadline": 1704211234,
                "tags": ["development", "frontend"],
            }
        }


class Contribution(BaseModel):
    """Deterministic contribution model."""

    contribution_id: str = Field(..., description="Deterministic contribution ID")
    bounty_id: str = Field(..., description="Bounty being contributed to")

    contributor_wallet: str = Field(..., description="Contributor wallet address")
    reference: str = Field(..., description="Reference (PR URL, commit hash, etc.)")

    submitted_at: int = Field(..., description="Deterministic timestamp")

    # Optional: proof of work
    proof: Optional[Dict] = Field(None, description="Proof of contribution")

    class Config:
        json_schema_extra = {
            "example": {
                "contribution_id": "contrib_bounty123_1703002000",
                "bounty_id": "bounty_space123_1703001234",
                "contributor_wallet": "0xdef...",
                "reference": "https://github.com/org/repo/pull/123",
                "submitted_at": 1703002000,
            }
        }


class RewardDecision(BaseModel):
    """Deterministic reward allocation decision."""

    bounty_id: str = Field(..., description="Bounty being rewarded")
    recipient_wallet: str = Field(..., description="Recipient wallet address")

    amount: float = Field(..., ge=0.0, description="Reward amount")
    percentage: float = Field(
        ..., ge=0.0, le=1.0, description="Percentage of total reward"
    )

    reason: str = Field(..., description="Deterministic reason for allocation")
    decided_at: int = Field(..., description="Deterministic decision timestamp")

    # Quality scores (from advisory layer or deterministic scoring)
    quality_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Quality score"
    )
    advisory_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Advisory score"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "bounty_id": "bounty_space123_1703001234",
                "recipient_wallet": "0xdef...",
                "amount": 650.0,
                "percentage": 0.65,
                "reason": "Highest quality score (0.85), normalized share: 65%",
                "decided_at": 1703100000,
                "quality_score": 0.85,
                "advisory_score": 0.80,
            }
        }


class BountyState(BaseModel):
    """Aggregate state of a bounty reconstructed from events."""

    bounty: Bounty
    contributions: List[Contribution] = Field(default_factory=list)
    reward_decisions: List[RewardDecision] = Field(default_factory=list)

    # Computed fields
    total_contributions: int = Field(
        default=0, description="Total number of contributions"
    )
    total_rewards_allocated: float = Field(
        default=0.0, description="Total rewards allocated"
    )

    # Advisory signals (from agent layer)
    advisory_signals: List[Dict] = Field(
        default_factory=list, description="Agent advisory events"
    )

    def compute_totals(self):
        """Compute totals deterministically."""
        self.total_contributions = len(self.contributions)
        self.total_rewards_allocated = sum(r.amount for r in self.reward_decisions)
