"""
AEGIS Sandbox Assistant - Track 5.3

Annotates sandbox results with pattern highlights and coaching hints.
References proof vectors and hashes for traceability.
"""

from typing import Dict, Any
from ..ui_contracts.schemas import SandboxResult, UserExplanationSettings


def analyze_sandbox_result(
    result: SandboxResult, user_settings: UserExplanationSettings
) -> SandboxResult:
    """
    Annotate sandbox result with AEGIS insights.

    Args:
        result: Raw execution result
        user_settings: User preferences

    Returns:
        Annotated result
    """
    if user_settings.mode == "OFF":
        return result

    annotations = {}

    # 1. Analyze Guard Events
    if result.guard_events:
        count = len(result.guard_events)
        annotations["guard_insight"] = (
            f"Simulation triggered {count} guard checks. "
            "This suggests high regulatory interaction."
        )

    # 2. Analyze Metrics
    risk = int(result.metrics.get("risk_score", "0"))
    if risk > 10:
        annotations["risk_alert"] = (
            "Risk score elevated. Consider reducing leverage param."
        )

    # 3. Add Coaching Hint (Heuristic)
    if "stress" in result.template_id:
        annotations["coaching"] = (
            "Stress tests help identify liquidity gaps. Try ensuring reserve > 20%."
        )

    result.annotations = annotations
    return result
