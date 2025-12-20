from typing import Protocol, Dict, Any, Optional


class DeterministicAdvisoryModel(Protocol):
    """
    Protocol for any Advisory Model in v17/v18.

    Contract:
    1. Must be deterministic: score(event) -> same_result for same input.
    2. Must be stateless: No side effects on F-layer.
    3. Must use explicit timestamps from the event payload.
    """

    def calculate_score(self, event_type: str, payload: Dict[str, Any]) -> float:
        """Return a normalized score [0.0, 1.0]"""
        ...

    def generate_flags(self, event_type: str, payload: Dict[str, Any]) -> list[str]:
        """Return a list of human-readable reason strings."""
        ...

    def model_version(self) -> str:
        """Return the version identifier string."""
        ...
