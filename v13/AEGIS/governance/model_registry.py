"""
Model Registry - Track 2.1

Manages AEGIS model configurations, versions, and governance.
All models must be registered and versioned for auditability.

Contract Compliance:
- Deterministic loading from JSON
- Versioned configs
- Immutable model definitions
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import json
from pathlib import Path


class AEGISModelConfig(BaseModel):
    """
    Configuration for an AEGIS advisory model.
    """

    model_id: str = Field(..., description="Unique model identifier")
    version: str = Field(..., description="Semantic version string")
    causal_graph_hash: str = Field(
        ..., description="Hash of the deterministic causal graph definition"
    )
    training_data_fingerprint: str = Field(
        ..., description="Hash/Fingerprint of training data/weights"
    )
    intended_use: str = Field(..., description="Description of intended use case")
    scope: List[str] = Field(
        ..., description="List of authorized scopes (e.g., 'governance', 'sandbox')"
    )
    constraints: Dict[str, str] = Field(
        ..., description="Operational constraints (e.g., 'max_tokens', 'timeout')"
    )


def _load_registry() -> Dict[str, AEGISModelConfig]:
    """
    Load the model registry from the JSON file.
    Memoized in function attribute.
    """
    if hasattr(_load_registry, "_cache") and _load_registry._cache:
        return _load_registry._cache

    registry_path = Path(__file__).with_name("aegis_model_registry.json")
    if not registry_path.exists():
        # Fallback/Bootstrap if file doesn't exist yet
        return {}

    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        # Store keys as "model_id@version"
        # Sort data for deterministic processing order if needed, though dicts are insertion ordered in modern python
        sorted_data = sorted(data, key=lambda x: (x["model_id"], x["version"]))

        configs = {
            f"{c['model_id']}@{c['version']}": AEGISModelConfig(**c)
            for c in sorted_data
        }
        _load_registry._cache = configs
        return configs
    except Exception:
        # Error loading registry - return empty dict (bootstrap mode)
        return {}


def get_model_config(model_id: str, version: str) -> Optional[AEGISModelConfig]:
    """
    Retrieve a specific model configuration.
    """
    key = f"{model_id}@{version}"
    registry = _load_registry()
    return registry.get(key)


def get_active_aegis_model() -> Optional[AEGISModelConfig]:
    """
    Retrieve the currently active AEGIS model.
    For Phase 1, this is hardcoded/bootstrapped. Later, this could be read from a governance state.
    """
    registry = _load_registry()
    # For now, pick a hardcoded active key as per Track 2.1 specs
    active_key = "hall_v1@0.1"
    return registry.get(active_key)
