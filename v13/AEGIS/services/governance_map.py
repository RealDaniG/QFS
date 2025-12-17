"""
Governance Consequence Map - Track 4

Deterministic DAG builder + advisory overlay for governance proposals.
Maps proposals → affected guards → economic modules → token metrics.

Contract Compliance:
- Uses only deterministic simulation via DRV replay
- Returns result with advisory=True
- Full traceability via proof vectors
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..ui_contracts.schemas import (
    GovernanceMapRequest,
    GovernanceMapResponse,
    DAGNode,
    DAGEdge,
)
from .evidence_service import find_proof_vectors_for_dag
from ..governance.model_registry import get_active_aegis_model
from .explanation_service import generate_aegis_explanation
from .explanation_control import generate_explanation_id

router = APIRouter()


def build_deterministic_graph(proposal_id: str) -> Tuple[List[DAGNode], List[DAGEdge]]:
    """
    Construct deterministic DAG of proposal impact.
    Track 4.2: Maps proposals to guards to modules.

    Args:
        proposal_id: ID of the proposal

    Returns:
        (nodes, edges) sorted lexicographically
    """
    # Mock implementation of deterministic logic
    # In production: query Policy Engine, map Guard registry

    nodes = []
    edges = []

    # 1. Proposal Node
    prop_node_id = f"proposal:{proposal_id}"
    nodes.append(
        DAGNode(
            node_id=prop_node_id,
            node_type="proposal",
            label="Proposal: " + proposal_id.replace("_", " ").title(),
            metadata={"status": "draft"},
        )
    )

    # 2. Simulate logic: If 'chr' in ID, it affects CHR guards
    if "chr" in proposal_id.lower():
        guard_id = "guard:EconomicsGuard_CHR_Caps"
        nodes.append(
            DAGNode(
                node_id=guard_id,
                node_type="guard",
                label="CHR Supply Cap Guard",
                metadata={"cir_code": "CIR-101"},
            )
        )
        edges.append(
            DAGEdge(from_node=prop_node_id, to_node=guard_id, edge_type="checks")
        )

        module_id = "module:TreasuryEngine"
        nodes.append(
            DAGNode(
                node_id=module_id,
                node_type="module",
                label="Treasury Engine",
                metadata={},
            )
        )
        edges.append(
            DAGEdge(from_node=guard_id, to_node=module_id, edge_type="protects")
        )

    # Sort for determinism
    nodes.sort(key=lambda x: x.node_id)
    edges.sort(key=lambda x: (x.from_node, x.to_node))

    return nodes, edges


@router.post("/governance/consequence_map", response_model=GovernanceMapResponse)
async def get_consequence_map(req: GovernanceMapRequest) -> GovernanceMapResponse:
    """
    Generate governance consequence map with AEGIS annotations.
    """
    # 1. Build deterministic graph (Core QFS logic)
    nodes, edges = build_deterministic_graph(req.proposal_id)

    # 2. Find evidence (Track 1)
    dag_descriptor = {"nodes": [n.node_id for n in nodes]}
    proof_refs = find_proof_vectors_for_dag(dag_descriptor)

    # 3. Get active model (Track 2)
    model = get_active_aegis_model()
    if not model:
        # Fallback if registry not loaded
        model_id = "unknown"
        version = "0.0"
    else:
        model_id = model.model_id
        version = model.version

    # 4. Generate explanation (Track 4.1)
    explanation_text, _meta = generate_aegis_explanation(
        dag=nodes, user_settings=req.user_settings, proof_refs=proof_refs
    )

    # 5. Compute deterministic ID (Track 3)
    exp_id = generate_explanation_id(nodes, proof_refs, model_id, req.user_settings)

    return GovernanceMapResponse(
        advisory=True,
        aegis_model_id=model_id,
        aegis_version=version,
        explanation_mode=req.user_settings.mode,
        explanation_text=explanation_text,
        proof_vector_refs=proof_refs,
        nodes=nodes,
        edges=edges,
        explanation_id=exp_id,
    )
