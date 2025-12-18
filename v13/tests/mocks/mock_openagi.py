from typing import List, Dict, Any
import time
from v13.libs.canonical.models import AdvisorySignal


class MockOpenAGIAgent:
    """
    Simulates an Open-A.G.I agent consuming the read-only API.
    """

    def generate_signal(
        self, signal_id: str, payload: Dict[str, Any]
    ) -> AdvisorySignal:
        """
        Produce a signed advisory signal complying with the canonical schema.
        """
        # In a real scenario, this would involve PQC signing.
        # Here we mock the signature.
        mock_signature = f"sig_pqc_{signal_id}_mock"

        return AdvisorySignal(
            signal_id=signal_id,
            issuer_id="mock_agent_001",
            payload=payload,
            signature=mock_signature,
            timestamp=int(time.time()),
        )
