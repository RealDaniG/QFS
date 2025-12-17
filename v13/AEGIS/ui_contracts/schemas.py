"""
AEGIS UI Contracts - Pydantic Schemas (Track 0.3)

API request/response schemas for AEGIS advisory layer.
All schemas maintain lexicographic ordering for determinism.

Contract Compliance:
- All responses include aegis_model_id + aegis_version
- All explanations include proof_vector_refs for traceability
- UserExplanationSettings control advisory mode (OFF/CAUSAL_ONLY/HEURISTIC_ALLOWED)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional


class ProofVectorRef(BaseModel):
    """
    Reference to a deterministic proof vector.

    Proof vectors are evidence artifacts from:
    - Explain-This framework
    - DRV replay logs
    - Guard observations
    - Simulation runs
    """

    id: str = Field(..., description="Unique proof vector ID")
    scenario_type: str = Field(
        ..., description="Type of scenario (e.g., 'guard_activation', 'economic_flow')"
    )
    log_hash: str = Field(..., description="SHA3-512 hash of proof vector log")
    state_hash: str = Field(
        ..., description="SHA3-512 hash of state at proof vector time"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "pv_chr_reward_001",
                "scenario_type": "economic_flow",
                "log_hash": "abc123...",
                "state_hash": "def456...",
            }
        }


class UserExplanationSettings(BaseModel):
    """
    User-configurable explanation settings.

    mode:
      - OFF: No AEGIS explanations, show only raw metrics
      - CAUSAL_ONLY: Deterministic causal explanations only (DAGs, proof vectors)
      - HEURISTIC_ALLOWED: Include ML-based pattern detection and recommendations

    verbosity:
      - MINIMAL: One-line summaries
      - STANDARD: Paragraph explanations with key points
      - DETAILED: Full breakdown with all proof vectors and edges
    """

    mode: Literal["OFF", "CAUSAL_ONLY", "HEURISTIC_ALLOWED"] = Field(
        default="CAUSAL_ONLY",
        description="Explanation mode controlling AI assistance level",
    )
    verbosity: Literal["MINIMAL", "STANDARD", "DETAILED"] = Field(
        default="STANDARD", description="Detail level of explanations"
    )

    class Config:
        json_schema_extra = {
            "example": {"mode": "CAUSAL_ONLY", "verbosity": "STANDARD"}
        }


class GovernanceMapRequest(BaseModel):
    """
    Request for governance consequence map.

    Flow:
    1. User views governance proposal
    2. Frontend requests consequence map with user settings
    3. Backend builds deterministic DAG + AEGIS annotations
    4. Frontend renders interactive graph
    """

    proposal_id: str = Field(..., description="Governance proposal ID")
    user_settings: UserExplanationSettings = Field(
        ..., description="User explanation preferences"
    )
    target_edges: Optional[List[str]] = Field(
        default=None,
        description="Optional: specific edges to analyze (for focused views)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "proposal_id": "prop_001_increase_chr_cap",
                "user_settings": {"mode": "CAUSAL_ONLY", "verbosity": "STANDARD"},
                "target_edges": ["guard_eco_001 -> module_treasury"],
            }
        }


class DAGNode(BaseModel):
    """
    Node in governance consequence DAG.

    Node types: proposal, guard, module, metric, token
    """

    node_id: str = Field(..., description="Unique node ID (format: type:identifier)")
    node_type: Literal["proposal", "guard", "module", "metric", "token"] = Field(
        ..., description="Node type"
    )
    label: str = Field(..., description="Human-readable label")
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Additional node metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "guard:EconomicsGuard_CHR_001",
                "node_type": "guard",
                "label": "CHR Daily Cap Guard",
                "metadata": {"cir_code": "CIR-101", "severity": "high"},
            }
        }


class DAGEdge(BaseModel):
    """
    Edge in governance consequence DAG.
    """

    from_node: str = Field(..., description="Source node ID")
    to_node: str = Field(..., description="Target node ID")
    edge_type: str = Field(
        ..., description="Relationship type (e.g., 'affects', 'enforces')"
    )
    weight: Optional[str] = Field(
        default=None, description="Optional edge weight for importance (Decimal string)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "from_node": "proposal:prop_001",
                "to_node": "guard:EconomicsGuard_CHR_001",
                "edge_type": "affects",
                "weight": "0.85",
            }
        }


class GovernanceMapResponse(BaseModel):
    """
    Response containing governance consequence map + AEGIS annotations.

    Contract Compliance:
    - advisory flag MUST be True
    - aegis_model_id + aegis_version MUST be included
    - proof_vector_refs MUST link to deterministic artifacts
    """

    advisory: Literal[True] = Field(
        default=True,
        description="REQUIRED: This is advisory data, not authoritative",
    )
    aegis_model_id: str = Field(..., description="AEGIS model used for annotations")
    aegis_version: str = Field(..., description="AEGIS model version")
    explanation_mode: str = Field(
        ..., description="Mode used (OFF/CAUSAL_ONLY/HEURISTIC_ALLOWED)"
    )

    # DAG structure (deterministic)
    nodes: List[DAGNode] = Field(
        ..., description="DAG nodes (lexicographically sorted by node_id)"
    )
    edges: List[DAGEdge] = Field(
        ..., description="DAG edges (sorted by from_node, then to_node)"
    )

    # AEGIS annotations (advisory)
    explanation_text: str = Field(..., description="Natural language explanation")
    proof_vector_refs: List[ProofVectorRef] = Field(
        ..., description="Proof vectors used for this explanation"
    )

    # Optional metadata
    explanation_id: Optional[str] = Field(
        default=None,
        description="Deterministic hash of (DAG + proof vectors + model + settings)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "advisory": True,
                "aegis_model_id": "aegis_base_v1",
                "aegis_version": "1.0.0",
                "explanation_mode": "CAUSAL_ONLY",
                "nodes": [],
                "edges": [],
                "explanation_text": "This proposal affects CHR daily cap guard...",
                "proof_vector_refs": [],
                "explanation_id": "exp_abc123...",
            }
        }


class SandboxScenarioRequest(BaseModel):
    """
    Request to run sandbox scenario (Track 5.2).
    """

    template_id: str = Field(..., description="Scenario template ID")
    params: Dict[str, str] = Field(
        ..., description="Scenario parameters (deterministic)"
    )
    user_settings: UserExplanationSettings = Field(
        ..., description="User explanation preferences"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "template_chr_reward_stress_test",
                "params": {"chr_reward_multiplier": "1.5"},
                "user_settings": {"mode": "CAUSAL_ONLY", "verbosity": "DETAILED"},
            }
        }


class SandboxResult(BaseModel):
    """
    Results from sandbox scenario execution (Track 5.1).

    Contract Compliance:
    - state_hashes MUST be deterministic (same inputs → same hashes)
    - No RealLedger writes (sandbox isolated)
    """

    scenario_id: str = Field(..., description="Unique sandbox run ID")
    template_id: str = Field(..., description="Template used")

    # Deterministic results
    state_hashes: List[str] = Field(..., description="State hashes at each step")
    guard_events: List[Dict[str, str]] = Field(
        ..., description="Guard activations during scenario"
    )
    metrics: Dict[str, str] = Field(
        ..., description="Final metric values (BigNum128 strings)"
    )

    # AEGIS annotations (advisory)
    annotations: Optional[Dict[str, str]] = Field(
        default=None, description="AEGIS pattern highlights and coaching hints"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "sandbox_run_001",
                "template_id": "template_chr_reward_stress_test",
                "state_hashes": ["hash1...", "hash2..."],
                "guard_events": [{"guard": "CHR_cap", "step": "5", "result": "passed"}],
                "metrics": {"total_chr_allocated": "15000.0"},
                "annotations": {"pattern_detected": "EA-3 (guard margin tight)"},
            }
        }


# Export all schemas
__all__ = [
    "ProofVectorRef",
    "UserExplanationSettings",
    "GovernanceMapRequest",
    "GovernanceMapResponse",
    "DAGNode",
    "DAGEdge",
    "SandboxScenarioRequest",
    "SandboxResult",
]
