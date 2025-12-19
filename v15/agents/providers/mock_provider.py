"""
Mock Agent Provider (v16 Baseline)

Deterministic mock implementation for testing and dev/beta environments.
Zero-cost, fully deterministic, MOCKQPC-compatible.
"""

import hashlib
from typing import Dict


class MockAgentProvider:
    """
    Mock agent provider for deterministic testing.

    In MOCKQPC mode, this provides deterministic "advisory" outputs
    based on simple heuristics, ensuring Zero-Sim compliance.
    """

    def __init__(self, provider_name: str = "mock", version: str = "v1.0.0"):
        self.provider_name = provider_name
        self.version = version

    def score_content(
        self,
        content_id: str,
        content_type: str,
        content_text: str,
    ) -> Dict:
        """
        Deterministic content scoring based on simple heuristics.

        Returns:
            ContentScoreAdvisory-compatible dict
        """
        # Deterministic scoring based on content hash
        content_hash = hashlib.sha256(content_text.encode()).hexdigest()
        hash_int = int(content_hash[:8], 16)

        # Normalize to 0-1 range (deterministic)
        quality_score = (hash_int % 100) / 100.0
        risk_score = ((hash_int // 100) % 100) / 100.0
        relevance_score = ((hash_int // 10000) % 100) / 100.0

        # Deterministic flags
        flags = []
        if quality_score > 0.7:
            flags.append("high_quality")
        if risk_score > 0.7:
            flags.append("needs_review")
        if len(content_text) < 10:
            flags.append("too_short")

        return {
            "content_id": content_id,
            "content_type": content_type,
            "quality_score": round(quality_score, 2),
            "risk_score": round(risk_score, 2),
            "relevance_score": round(relevance_score, 2),
            "flags": flags,
            "confidence": 0.85,  # Mock confidence
            "agent_provider": self.provider_name,
            "model_version": self.version,
            "reasoning": f"Mock deterministic scoring based on content hash",
        }

    def recommend(
        self,
        entity_id: str,
        entity_type: str,
        context: Dict,
    ) -> Dict:
        """
        Deterministic recommendation based on entity ID hash.

        Returns:
            RecommendationAdvisory-compatible dict
        """
        # Deterministic recommendation
        entity_hash = hashlib.sha256(entity_id.encode()).hexdigest()
        hash_int = int(entity_hash[:8], 16)

        # Deterministic recommendation type
        rec_types = ["approve", "reject", "needs_review", "escalate"]
        recommendation_type = rec_types[hash_int % len(rec_types)]

        # Deterministic priority
        priorities = ["low", "medium", "high", "critical"]
        priority = priorities[(hash_int // 4) % len(priorities)]

        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "recommendation_type": recommendation_type,
            "priority": priority,
            "confidence": 0.80,
            "agent_provider": self.provider_name,
            "model_version": self.version,
            "reasoning": f"Mock deterministic recommendation based on entity hash",
            "supporting_data": context,
        }

    def assess_risk(
        self,
        entity_id: str,
        entity_type: str,
        context: Dict,
    ) -> Dict:
        """
        Deterministic risk assessment based on entity ID hash.

        Returns:
            RiskFlagAdvisory-compatible dict
        """
        # Deterministic risk assessment
        entity_hash = hashlib.sha256(entity_id.encode()).hexdigest()
        hash_int = int(entity_hash[:8], 16)

        # Deterministic risk type
        risk_types = ["spam", "abuse", "manipulation", "anomaly", "security"]
        risk_type = risk_types[hash_int % len(risk_types)]

        # Deterministic severity
        severities = ["low", "medium", "high", "critical"]
        severity = severities[(hash_int // 5) % len(severities)]

        # Deterministic indicators
        indicators = []
        if hash_int % 2 == 0:
            indicators.append("unusual_pattern")
        if hash_int % 3 == 0:
            indicators.append("rapid_activity")

        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "risk_type": risk_type,
            "severity": severity,
            "confidence": 0.75,
            "agent_provider": self.provider_name,
            "model_version": self.version,
            "indicators": indicators,
            "reasoning": f"Mock deterministic risk assessment based on entity hash",
        }
