"""
Explanation Service - Track 4.1

Generates Hall-aligned narrative explanations based on:
- Deterministic DAGs
- Proof vectors
- User settings (mode, verbosity)

Contract Compliance:
- Explanations are advisory only
- Narratives derived ONLY from deterministic inputs (DAG nodes, proof vectors)
- Traceability metadata included
"""

from typing import Tuple, List, Dict, Any
from ..ui_contracts.schemas import UserExplanationSettings, DAGNode, ProofVectorRef


def generate_aegis_explanation(
    dag: List[DAGNode],
    user_settings: UserExplanationSettings,
    proof_refs: List[ProofVectorRef],
) -> Tuple[str, Dict[str, Any]]:
    """
    Generate natural language explanation.

    Args:
        dag: Deterministic DAG nodes
        user_settings: User preferences
        proof_refs: Evidence used

    Returns:
        (explanation_text, metadata)
    """
    if user_settings.mode == "OFF":
        return "Advisory explanations disabled.", {}

    # Build narrative based on DAG analysis
    # In a real system, this would use templates or constrained LM generation
    # based on the graph structure.

    affected_nodes = [n for n in dag if n.node_type == "guard"]
    affected_modules = [n for n in dag if n.node_type == "module"]

    # Simple deterministic template logic
    if not affected_nodes:
        text = "This proposal does not appear to directly trigger any known constitutional guards."
    else:
        guards_str = ", ".join([n.label for n in affected_nodes])
        text = f"This proposal interacts with {len(affected_nodes)} constitutional guards: {guards_str}."

        if user_settings.verbosity == "DETAILED":
            text += (
                f" It functionally impacts {len(affected_modules)} economic modules."
            )
            text += f" Evidence is provided by {len(proof_refs)} proof vectors."

    # Traceability metadata
    meta = {
        "node_count": len(dag),
        "proof_count": len(proof_refs),
        "generator": "heuristic_template_v1",
    }

    return text, meta
