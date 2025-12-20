from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AdvisorySignal(BaseModel):
    """
    Standard schema for all v17 Agent Advisory signals.
    """

    target_type: str = Field(
        ..., description="Type of entity being advised on (proposal, bounty, social)"
    )
    target_id: str = Field(..., description="ID of the entity")
    score: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized score (risk, quality, urgency)"
    )
    reasons: List[str] = Field(
        default_factory=list, description="Human-readable reasons for the score"
    )
    model_version: str = Field(
        ..., description="Identifier of the deterministic model used"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )
