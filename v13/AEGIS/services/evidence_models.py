"""
Evidence Models - Track 1.1

Detailed data models for deterministic proof vectors and evidence artifacts.
Used internally by AEGIS services to construct verifiable explanations.

Contract Compliance:
- Fully deterministic fields
- Hash-linked to ledger/logs
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class GuardEvent(BaseModel):
    """Event triggered by a Constitutional Guard."""

    guard_id: str
    step: str
    result: str  # PASSED / BLOCKED / WARNING
    details: Dict[str, str]


class ProofVector(BaseModel):
    """
    Complete deterministic proof vector containing all evidence
    needed to verify a specific outcome.
    """

    id: str = Field(..., description="Unique ID (deterministic hash usually)")
    scenario_type: str = Field(
        ..., description="Context type (e.g., reward, governance)"
    )

    # Deterministic Inputs & Outputs
    input_params: Dict[str, str] = Field(..., description="stable stringified inputs")
    outputs: Dict[str, str] = Field(..., description="Stable stringified outputs")

    # Audit Trail
    guard_events: List[GuardEvent] = Field(default_factory=list)
    state_hashes: List[str] = Field(..., description="Ledger state hashes accessed")
    log_hashes: List[str] = Field(..., description="Transaction log hashes")

    # Provenance
    source_module: str = Field(..., description="Module that produced this vector")
    timestamp: str = Field(..., description="ISO 8601 deterministic timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "pv_12345",
                "scenario_type": "transaction_validation",
                "input_params": {"amount": "100", "sender": "user_a"},
                "outputs": {"status": "accepted", "fee": "0.1"},
                "guard_events": [],
                "state_hashes": ["hash_state_pre", "hash_state_post"],
                "log_hashes": ["hash_tx_log"],
                "source_module": "v13.core.TransactionEngine",
                "timestamp": "2025-12-17T12:00:00Z",
            }
        }
