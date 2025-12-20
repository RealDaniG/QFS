"""
Advisory Router (v16 Baseline)

Interface between EvidenceBus and external agent providers.
Ensures all agent outputs are PoE-logged and non-authoritative.
"""

from typing import Dict, List, Optional

from v15.evidence.bus import EvidenceBus
from v15.agents.schemas import (
    AgentAdvisoryEvent,
    ContentScoreAdvisory,
    RecommendationAdvisory,
    RiskFlagAdvisory,
)


class AdvisoryRouter:
    """
    Routes advisory requests to agent providers and logs results to EvidenceBus.

    Key principles:
    - Agents are read-only; they consume EvidenceBus events as input
    - All agent outputs are logged as AGENT_ADVISORY events
    - F (deterministic functions) remains the only authority for decisions
    """

    def __init__(self):
        self.bus = EvidenceBus
        self.providers = {}  # Registry of agent providers

    def register_provider(self, name: str, provider):
        """Register an agent provider (CrewAI, LangGraph, etc.)."""
        self.providers[name] = provider

    def request_content_score(
        self,
        content_id: str,
        content_type: str,
        content_text: str,
        provider: str = "mock",
        timestamp: int = 0,
    ) -> Dict:
        """
        Request content scoring from an agent provider.

        Args:
            content_id: ID of content to score
            content_type: Type of content (post, comment, etc.)
            content_text: The actual content text
            provider: Agent provider to use
            timestamp: Deterministic timestamp

        Returns:
            Advisory event envelope from EvidenceBus
        """
        # Get provider
        agent_provider = self.providers.get(provider)
        if not agent_provider:
            raise ValueError(f"Unknown provider: {provider}")

        # Call agent (read-only)
        advisory_result = agent_provider.score_content(
            content_id=content_id,
            content_type=content_type,
            content_text=content_text,
        )

        # Wrap in schema
        content_score = ContentScoreAdvisory(**advisory_result)

        # Create advisory event
        advisory_event = AgentAdvisoryEvent(
            advisory_type="content_score",
            content_score=content_score,
            timestamp=timestamp,
            related_events=[],  # Could link to original content event
        )

        # Emit to EvidenceBus (PoE-logged)
        envelope = self.bus.emit(
            "AGENT_ADVISORY",
            {
                "advisory": advisory_event.model_dump(),
                "timestamp": timestamp,
            },
        )

        return envelope

    def request_recommendation(
        self,
        entity_id: str,
        entity_type: str,
        context: Dict,
        provider: str = "mock",
        timestamp: int = 0,
    ) -> Dict:
        """
        Request recommendation from an agent provider.

        Args:
            entity_id: ID of entity (bounty, proposal, etc.)
            entity_type: Type of entity
            context: Context data for the agent
            provider: Agent provider to use
            timestamp: Deterministic timestamp

        Returns:
            Advisory event envelope from EvidenceBus
        """
        agent_provider = self.providers.get(provider)
        if not agent_provider:
            raise ValueError(f"Unknown provider: {provider}")

        # Call agent
        advisory_result = agent_provider.recommend(
            entity_id=entity_id,
            entity_type=entity_type,
            context=context,
        )

        # Wrap in schema
        recommendation = RecommendationAdvisory(**advisory_result)

        # Create advisory event
        advisory_event = AgentAdvisoryEvent(
            advisory_type="recommendation",
            recommendation=recommendation,
            timestamp=timestamp,
            related_events=[],
        )

        # Emit to EvidenceBus
        envelope = self.bus.emit(
            "AGENT_ADVISORY",
            {
                "advisory": advisory_event.model_dump(),
                "timestamp": timestamp,
            },
        )

        return envelope

    def request_risk_assessment(
        self,
        entity_id: str,
        entity_type: str,
        context: Dict,
        provider: str = "mock",
        timestamp: int = 0,
    ) -> Dict:
        """
        Request risk assessment from an agent provider.

        Args:
            entity_id: ID of entity to assess
            entity_type: Type of entity
            context: Context data for assessment
            provider: Agent provider to use
            timestamp: Deterministic timestamp

        Returns:
            Advisory event envelope from EvidenceBus
        """
        agent_provider = self.providers.get(provider)
        if not agent_provider:
            raise ValueError(f"Unknown provider: {provider}")

        # Call agent
        advisory_result = agent_provider.assess_risk(
            entity_id=entity_id,
            entity_type=entity_type,
            context=context,
        )

        # Wrap in schema
        risk_flag = RiskFlagAdvisory(**advisory_result)

        # Create advisory event
        advisory_event = AgentAdvisoryEvent(
            advisory_type="risk_flag",
            risk_flag=risk_flag,
            timestamp=timestamp,
            related_events=[],
        )

        # Emit to EvidenceBus
        envelope = self.bus.emit(
            "AGENT_ADVISORY",
            {
                "advisory": advisory_event.model_dump(),
                "timestamp": timestamp,
            },
        )

        return envelope

    def get_advisory_history(
        self,
        entity_id: Optional[str] = None,
        advisory_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get advisory history from EvidenceBus.

        Args:
            entity_id: Optional filter by entity ID
            advisory_type: Optional filter by advisory type
            limit: Max events to return

        Returns:
            List of advisory events
        """
        all_events = self.bus.get_events(limit=limit * 2)

        # Filter for AGENT_ADVISORY events
        advisory_events = []
        for e in all_events:
            if (
                isinstance(e, dict)
                and e.get("event", {}).get("type") == "AGENT_ADVISORY"
            ):
                advisory_events.append(e)

        # Apply filters
        if entity_id or advisory_type:
            filtered = []
            for e in advisory_events:
                if not isinstance(e, dict):
                    continue

                event_data = e.get("event", {})
                if not isinstance(event_data, dict):
                    continue

                payload = event_data.get("payload", {})
                if not isinstance(payload, dict):
                    continue

                advisory_data = payload.get("advisory", {})
                if not isinstance(advisory_data, dict):
                    continue

                # Filter by type
                if (
                    advisory_type
                    and advisory_data.get("advisory_type") != advisory_type
                ):
                    continue

                # Filter by entity
                if entity_id:
                    # Check all possible entity ID fields
                    content_score = advisory_data.get("content_score", {})
                    recommendation = advisory_data.get("recommendation", {})
                    risk_flag = advisory_data.get("risk_flag", {})

                    if not (
                        (
                            isinstance(content_score, dict)
                            and content_score.get("content_id") == entity_id
                        )
                        or (
                            isinstance(recommendation, dict)
                            and recommendation.get("entity_id") == entity_id
                        )
                        or (
                            isinstance(risk_flag, dict)
                            and risk_flag.get("entity_id") == entity_id
                        )
                    ):
                        continue

                filtered.append(e)

            advisory_events = filtered

        return advisory_events[:limit]
