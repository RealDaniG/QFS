"""
Agent Advisory Schemas (v16 Baseline)

Pydantic models for agent advisory events.
All advisory outputs are non-authoritative suggestions only.
"""

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class ContentScoreAdvisory(BaseModel):
    """Advisory signal for content quality/risk scoring."""

    content_id: str = Field(..., description="ID of the content being scored")
    content_type: Literal["post", "comment", "message", "proposal"] = Field(
        ..., description="Type of content"
    )

    # Multi-dimensional scoring
    quality_score: float = Field(
        ..., ge=0.0, le=1.0, description="Quality assessment (0-1)"
    )
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk assessment (0-1)")
    relevance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Relevance to context (0-1)"
    )

    # Advisory flags (non-binding)
    flags: List[str] = Field(
        default_factory=list,
        description="Advisory flags (e.g., 'needs_review', 'high_quality')",
    )

    # Confidence and provenance
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Agent confidence in assessment"
    )
    agent_provider: str = Field(
        ..., description="Agent provider (e.g., 'crewai', 'langgraph')"
    )
    model_version: str = Field(..., description="Model/version used")

    # Context
    reasoning: Optional[str] = Field(
        None, description="Optional explanation of scoring"
    )


class RecommendationAdvisory(BaseModel):
    """Advisory signal for recommendations (bounties, proposals, etc.)."""

    entity_id: str = Field(..., description="ID of entity being recommended on")
    entity_type: Literal["bounty", "proposal", "user", "space"] = Field(
        ..., description="Type of entity"
    )

    recommendation_type: Literal["approve", "reject", "needs_review", "escalate"] = (
        Field(..., description="Type of recommendation")
    )

    priority: Literal["low", "medium", "high", "critical"] = Field(
        default="medium", description="Suggested priority"
    )

    # Advisory metadata
    confidence: float = Field(..., ge=0.0, le=1.0, description="Agent confidence")
    agent_provider: str = Field(..., description="Agent provider")
    model_version: str = Field(..., description="Model/version used")

    reasoning: Optional[str] = Field(None, description="Explanation of recommendation")
    supporting_data: Optional[Dict] = Field(None, description="Additional context data")


class RiskFlagAdvisory(BaseModel):
    """Advisory signal for risk/anomaly detection."""

    entity_id: str = Field(..., description="ID of flagged entity")
    entity_type: str = Field(..., description="Type of entity")

    risk_type: Literal["spam", "abuse", "manipulation", "anomaly", "security"] = Field(
        ..., description="Type of risk detected"
    )

    severity: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Suggested severity"
    )

    # Advisory metadata
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    agent_provider: str = Field(..., description="Agent provider")
    model_version: str = Field(..., description="Model/version used")

    indicators: List[str] = Field(
        default_factory=list, description="Risk indicators detected"
    )
    reasoning: Optional[str] = Field(None, description="Explanation of risk assessment")


class AgentAdvisoryEvent(BaseModel):
    """
    Wrapper for all agent advisory events.
    This gets serialized into EvidenceBus as 'AGENT_ADVISORY' type.
    """

    advisory_type: Literal["content_score", "recommendation", "risk_flag"] = Field(
        ..., description="Type of advisory"
    )

    # One of these will be populated based on advisory_type
    content_score: Optional[ContentScoreAdvisory] = None
    recommendation: Optional[RecommendationAdvisory] = None
    risk_flag: Optional[RiskFlagAdvisory] = None

    # Metadata
    timestamp: int = Field(..., description="Deterministic timestamp")
    related_events: List[str] = Field(
        default_factory=list,
        description="Hashes of related EvidenceBus events that informed this advisory",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "advisory_type": "content_score",
                "content_score": {
                    "content_id": "post_123",
                    "content_type": "post",
                    "quality_score": 0.85,
                    "risk_score": 0.15,
                    "relevance_score": 0.90,
                    "flags": ["high_quality"],
                    "confidence": 0.92,
                    "agent_provider": "crewai",
                    "model_version": "v1.0.0",
                },
                "timestamp": 1703001234,
                "related_events": ["abc123..."],
            }
        }
