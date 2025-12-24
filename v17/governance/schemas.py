"""
Governance Schemas (v17 Beta)

Pydantic models for deterministic governance operations.
All state transitions are pure functions consuming EvidenceBus history.
"""

from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field
from v13.libs.BigNum128 import BigNum128


class GovernanceConfig(BaseModel):
    """Configuration for governance parameters."""

    quorum_threshold: str = Field(
        ..., description="Minimum participation rate (0-1) as BigNum128 decimal string"
    )
    approval_threshold: str = Field(
        ..., description="Minimum approval rate (0-1) as BigNum128 decimal string"
    )
    voting_period_seconds: int = Field(
        ..., gt=0, description="Duration of voting period"
    )
    execution_delay_seconds: int = Field(
        default=0, ge=0, description="Delay before execution"
    )

    allowed_choices: List[str] = Field(
        default=["approve", "reject", "abstain"], description="Valid vote choices"
    )

    tie_break_rule: Literal["reject", "approve", "extend"] = Field(
        default="reject", description="Deterministic tie-breaking rule"
    )


class Proposal(BaseModel):
    """Deterministic proposal model."""

    proposal_id: str = Field(..., description="Deterministic proposal ID")
    space_id: str = Field(..., description="Space where proposal was created")
    creator_wallet: str = Field(..., description="Wallet address of creator")

    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=10000)

    created_at: int = Field(..., description="Deterministic timestamp")
    voting_ends_at: int = Field(..., description="Deterministic end timestamp")

    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional proposal data"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "proposal_id": "prop_space123_1703001234",
                "space_id": "space_123",
                "creator_wallet": "0xabc...",
                "title": "Increase emission cap",
                "body": "Proposal to increase...",
                "created_at": 1703001234,
                "voting_ends_at": 1703087634,
                "metadata": {"category": "economic"},
            }
        }


class Vote(BaseModel):
    """Deterministic vote model."""

    proposal_id: str = Field(..., description="Proposal being voted on")
    voter_wallet: str = Field(..., description="Wallet address of voter")

    choice: str = Field(..., description="Vote choice (approve/reject/abstain)")
    weight: str = Field(
        default="1.000000000000000000", description="Vote weight (BigNum128 string)"
    )

    timestamp: int = Field(..., description="Deterministic timestamp")

    # Optional: signature proof (for verification)
    signature: Optional[str] = Field(None, description="EIP-191 signature of vote")

    class Config:
        json_schema_extra = {
            "example": {
                "proposal_id": "prop_space123_1703001234",
                "voter_wallet": "0xdef...",
                "choice": "approve",
                "weight": "1.000000000000000000",
                "timestamp": 1703002000,
            }
        }


class ProposalState(BaseModel):
    """Aggregate state of a proposal reconstructed from events."""

    proposal: Proposal
    votes: List[Vote] = Field(default_factory=list)

    # Computed fields
    total_votes: int = Field(default=0, description="Total number of votes cast")
    total_weight: str = Field(
        default="0.000000000000000000", description="Total vote weight"
    )

    approve_weight: str = Field(
        default="0.000000000000000000", description="Weight of approve votes"
    )
    reject_weight: str = Field(
        default="0.000000000000000000", description="Weight of reject votes"
    )
    abstain_weight: str = Field(
        default="0.000000000000000000", description="Weight of abstain votes"
    )

    # Advisory signals (from agent layer)
    advisory_signals: List[Dict[str, Any]] = Field(
        default_factory=list, description="Agent advisory events"
    )

    def compute_tallies(self):
        """Compute vote tallies deterministically."""
        self.total_votes = len(self.votes)

        # Use BigNum128 for summation
        total_bn = sum(
            (BigNum128.from_string(v.weight) for v in self.votes), BigNum128.zero()
        )
        self.total_weight = str(total_bn)

        approve_bn = sum(
            (
                BigNum128.from_string(v.weight)
                for v in self.votes
                if v.choice == "approve"
            ),
            BigNum128.zero(),
        )
        reject_bn = sum(
            (
                BigNum128.from_string(v.weight)
                for v in self.votes
                if v.choice == "reject"
            ),
            BigNum128.zero(),
        )
        abstain_bn = sum(
            (
                BigNum128.from_string(v.weight)
                for v in self.votes
                if v.choice == "abstain"
            ),
            BigNum128.zero(),
        )

        self.approve_weight = str(approve_bn)
        self.reject_weight = str(reject_bn)
        self.abstain_weight = str(abstain_bn)


class ExecutionRecord(BaseModel):
    """Record of proposal execution outcome."""

    proposal_id: str = Field(..., description="Proposal that was executed")

    final_outcome: Literal["approved", "rejected", "no_quorum", "tie"] = Field(
        ..., description="Final deterministic outcome"
    )

    executed_at: int = Field(..., description="Deterministic execution timestamp")

    # Vote statistics
    total_votes: int = Field(..., description="Total votes cast")
    total_weight: str = Field(..., description="Total vote weight")
    approve_weight: str = Field(..., description="Approve vote weight")
    reject_weight: str = Field(..., description="Reject vote weight")

    # Execution details
    effects: Optional[Dict[str, Any]] = Field(
        None, description="Deterministic effects applied"
    )
    reason: str = Field(..., description="Explanation of outcome")

    class Config:
        json_schema_extra = {
            "example": {
                "proposal_id": "prop_space123_1703001234",
                "final_outcome": "approved",
                "executed_at": 1703087634,
                "total_votes": 100,
                "total_weight": 100.0,
                "approve_weight": 65.0,
                "reject_weight": 35.0,
                "effects": {"emission_cap": 1000000},
                "reason": "Quorum met (100%), approval threshold met (65% > 50%)",
            }
        }
