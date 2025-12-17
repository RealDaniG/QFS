"""
Counter-Scenario Service - Track 3.4

Handles interactive "What-If" scenarios.
Flow: User overrides params → Sandbox simulates → AEGIS explains new result.

Contract Compliance:
- Uses isolated Sandbox (Track 5)
- Returns purely advisory data
"""

from typing import Dict, Any
from ..ui_contracts.schemas import GovernanceMapResponse, UserExplanationSettings
# from ..sandbox.engine import run_sandbox_scenario  # Will exist in Track 5


def run_counter_scenario(
    proposal_id: str,
    parameter_overrides: Dict[str, str],
    user_settings: UserExplanationSettings,
) -> GovernanceMapResponse:
    """
    Execute a counter-scenario and return the explanation.
    """
    # 1. Create modified proposal config (deterministic)
    # 2. Run deterministic simulation (Track 5)
    # 3. Generate explanation for new outcome

    # Mock response for now until Track 5 is ready
    return GovernanceMapResponse(
        advisory=True,
        aegis_model_id="hall_v1",
        aegis_version="0.1",
        explanation_mode=user_settings.mode,
        nodes=[],
        edges=[],
        explanation_text=f"Counter-scenario simulation for {proposal_id} with {parameter_overrides}",
        proof_vector_refs=[],
        explanation_id="exp_counter_mock_123",
    )
