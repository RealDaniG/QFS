"""
AEGIS Consequence Graph - Track 2.3

Builds a deterministic graph showing how AEGIS models affect UIs and decision flows.
Used for "Meta-Governance" - visualizing the impact of upgrading the AI itself.

Contract Compliance:
- Fully deterministic graph generation
- Visualizes advisory relationships only
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from ..ui_contracts.schemas import DAGNode, DAGEdge
from .model_registry import get_model_config


class AEGISConsequenceGraph(BaseModel):
    """
    Graph showing downstream impact of an AEGIS model.
    """

    model_id: str
    version: str
    nodes: List[DAGNode]
    edges: List[DAGEdge]


def build_aegis_consequence_graph(model_id: str, version: str) -> AEGISConsequenceGraph:
    """
    Construct deterministic graph of AEGIS model impact.

    Args:
        model_id: AEGIS model ID
        version: AEGIS model version

    Returns:
        Graph connecting Model -> Scopes -> UIs -> User Decisions
    """
    config = get_model_config(model_id, version)
    if not config:
        raise ValueError(f"Model config not found: {model_id}@{version}")

    nodes = []
    edges = []

    # 1. Root Node: The Model
    model_node_id = f"model:{model_id}@{version}"
    nodes.append(
        DAGNode(
            node_id=model_node_id,
            node_type="module",  # treating model as a module source
            label=f"AEGIS Model: {model_id} v{version}",
            metadata={"hash": config.causal_graph_hash},
        )
    )

    # 2. Scope Nodes (e.g., "governance_map")
    for scope in config.scope:
        scope_node_id = f"scope:{scope}"
        # Check if node already exists to avoid duplicates
        if not any(n.node_id == scope_node_id for n in nodes):
            nodes.append(
                DAGNode(
                    node_id=scope_node_id,
                    node_type="module",
                    label=f"Scope: {scope}",
                    metadata={"type": "capability"},
                )
            )

        # Edge: Model -> Scope
        edges.append(
            DAGEdge(from_node=model_node_id, to_node=scope_node_id, edge_type="enables")
        )

        # 3. UI/Feature Nodes derived from Scope
        # Static mapping of Scope -> UI features
        ui_features = _get_downstream_features(scope)
        for feature, desc in ui_features.items():
            feature_node_id = f"ui:{feature}"
            if not any(n.node_id == feature_node_id for n in nodes):
                nodes.append(
                    DAGNode(
                        node_id=feature_node_id,
                        node_type="proposal",  # borrowing type
                        label=f"UI: {desc}",
                        metadata={"layer": "frontend"},
                    )
                )

            # Edge: Scope -> UI
            edges.append(
                DAGEdge(
                    from_node=scope_node_id, to_node=feature_node_id, edge_type="powers"
                )
            )

    # Sort for determinism
    nodes.sort(key=lambda x: x.node_id)
    edges.sort(key=lambda x: (x.from_node, x.to_node))

    return AEGISConsequenceGraph(
        model_id=model_id, version=version, nodes=nodes, edges=edges
    )


def _get_downstream_features(scope: str) -> Dict[str, str]:
    """Static mapping of scopes to downstream UI features."""
    mapping = {
        "governance_map": {
            "consequence_map": "Governance Consequence Map",
            "risk_badges": "Risk Assessment Badges",
        },
        "reflection_panel": {
            "reflection_tabs": "Economic Action Reflection Panel",
            "principle_linking": "Constitutional Principle Links",
        },
        "sandbox": {
            "sandbox_assistant": "Sandbox AI Coach",
            "scenario_generation": "Scenario Generator",
        },
    }
    return mapping.get(scope, {})
