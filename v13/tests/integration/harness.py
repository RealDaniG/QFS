from typing import List, Dict, Any, Optional
from v13.libs.canonical.models import (
    UserIdentity,
    ContentMetadata,
    EconomicEvent,
    AdvisorySignal,
    ContentType,
)
from v13.tests.mocks.mock_atlas import MockAtlasFrontend
from v13.tests.mocks.mock_openagi import MockOpenAGIAgent
from v13.libs.BigNum128 import BigNum128


class SimulationHarness:
    """
    Orchestrates end-to-end simulation of the QFS ecosystem.
    Connects ATLAS User inputs -> QFS Logic -> Open-A.G.I Signals.
    """

    def __init__(self):
        self.atlas = MockAtlasFrontend()
        self.openagi = MockOpenAGIAgent()
        self.ledger: List[EconomicEvent] = []
        self.content_store: Dict[str, ContentMetadata] = {}
        self.signals: List[AdvisorySignal] = []

    def register_user(self, user_id: str, wallet: str) -> UserIdentity:
        """
        Simulate user onboarding.
        """
        return UserIdentity(
            user_id=user_id,
            wallet_address=wallet,
            public_key=f"pub_{user_id}",
            profile={"status": "active"},
        )

    def simulate_content_lifecycle(
        self, user: UserIdentity, content_id: str, data: Dict[str, Any]
    ):
        """
        1. User posts content via ATLAS.
        2. QFS calculates reward (simulated).
        3. Event is logged.
        """
        # 1. Create Content
        metadata = self.atlas.create_post(content_id, user.user_id, data)
        self.content_store[content_id] = metadata

        # 2. Calculate Reward (Mock Logic using BigNum128)
        # Base reward = 10.0 QFS * 1e18
        base_reward = BigNum128(10 * BigNum128.SCALE)

        # 3. Log Economic Event
        event = EconomicEvent(
            event_id=f"evt_reward_{content_id}",
            source_id="SYSTEM_TREASURY",
            target_id=user.user_id,
            amount=str(base_reward.value),  # Canonical string representation
            token_type="QFS",
            reason="CONTENT_MINING",
            timestamp=metadata.timestamp,
        )
        self.ledger.append(event)
        return event

    def simulate_agent_observation(self, content_id: str) -> Optional[AdvisorySignal]:
        """
        4. Open-A.G.I agent observes content and issues signal.
        """
        if content_id not in self.content_store:
            return None

        content = self.content_store[content_id]

        # Agent Logic
        payload = {
            "target_content": content_id,
            "sentiment": "positive",
            "coherence_score": 0.98,
        }

        signal = self.openagi.generate_signal(f"sig_{content_id}", payload)
        self.signals.append(signal)
        return signal
