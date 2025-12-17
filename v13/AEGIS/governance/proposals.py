"""
AEGIS Proposals - Track 2.2

Governance proposals for changes to AEGIS models, thresholds, or narrative styles.
Integrates with the main QFS governance system.

Contract Compliance:
- All changes to advisory models must go through governance
- Validation via proof vectors required
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class AEGISProposal(BaseModel):
    """
    Proposal to update an AEGIS model or configuration.
    """

    target_model_id: str = Field(..., description="ID of the model to update")
    target_version: str = Field(..., description="New version string")
    change_summary: str = Field(..., description="Human-readable summary of changes")

    # Evidence requirement
    validation_proof_vectors: List[str] = Field(
        ...,
        description="IDs of proof vectors demonstrating the change is safe/beneficial",
    )

    risk_assessment: str = Field(..., description="Self-assessment of risks")

    # Scope control
    scope_changes: Dict[str, str] = Field(
        default_factory=dict,
        description="Changes to authorized scope (e.g., {'added': 'sandbox', 'removed': 'none'})",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "target_model_id": "hall_v1",
                "target_version": "0.2",
                "change_summary": "Improved coherence weighting in governance map",
                "validation_proof_vectors": ["pv_test_run_01", "pv_test_run_02"],
                "risk_assessment": "Low - advisory only, no economic mutation",
                "scope_changes": {"added": "reflection_panel"},
            }
        }
