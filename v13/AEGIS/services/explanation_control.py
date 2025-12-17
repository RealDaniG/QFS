"""
Explanation Control Service - Track 3

Handles user settings, explanation provenance inspection, and counter-scenarios.
Provides transparency into WHY AEGIS produced a specific explanation.

Contract Compliance:
- Settings are per-user, non-consensus
- Explanation IDs are deterministic hashes of inputs
"""

import hashlib
import json
from typing import Dict, Any, Optional
from ..ui_contracts.schemas import UserExplanationSettings, GovernanceMapResponse

# Mock storage for user settings (In production: PostgreSQL/Redis)
_SETTINGS_DB: Dict[str, UserExplanationSettings] = {}


def get_user_settings(user_id: str) -> UserExplanationSettings:
    """Retrieve settings for user, returning defaults if not found."""
    return _SETTINGS_DB.get(
        user_id, UserExplanationSettings(mode="CAUSAL_ONLY", verbosity="STANDARD")
    )


def update_user_settings(user_id: str, settings: UserExplanationSettings):
    """Update user settings."""
    _SETTINGS_DB[user_id] = settings


def generate_explanation_id(
    dag_nodes: list,
    proof_vectors: list,
    model_id: str,
    settings: UserExplanationSettings,
) -> str:
    """
    Compute deterministic explanation ID based on all inputs.
    ID = SHA3-256(dag_hash + proofs_hash + model_id + settings)
    """
    hasher = hashlib.sha3_256()

    # Hash DAG (mock logic - assuming nodes sorted)
    dag_str = "".join([n.node_id for n in dag_nodes])
    hasher.update(dag_str.encode("utf-8"))

    # Hash proofs
    proofs_str = "".join([pv.id for pv in proof_vectors])
    hasher.update(proofs_str.encode("utf-8"))

    # Hash context
    context = f"{model_id}:{settings.mode}:{settings.verbosity}"
    hasher.update(context.encode("utf-8"))

    return hasher.hexdigest()


def get_explanation_meta(explanation_id: str) -> Dict[str, Any]:
    """
    Inspector: Retrieve metadata for a specific explanation ID.
    (Mock implementation - in real system would query historical logs)
    """
    # Used for "Why this explanation?" tooltip
    return {
        "explanation_id": explanation_id,
        "aegis_model_id": "hall_v1",
        "aegis_version": "0.1",
        "mode": "CAUSAL_ONLY",
        "used_proof_vectors": ["pv_mock_01", "pv_mock_02"],
        "used_metrics": ["chr_supply", "guard_activations"],
        "timestamp": "2025-12-17T12:00:00Z",
    }
