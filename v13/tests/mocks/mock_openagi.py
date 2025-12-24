from typing import Dict, Any
from v13.libs.deterministic_helpers import det_time_now
from v13.libs.canonical.models import AdvisorySignal


class MockOpenAGIAgent:
    """
    Simulates an Open-A.G.I agent consuming the read-only API.
    Uses deterministic timestamp for Zero-Sim compliance.
    """

    def generate_signal(
        self, signal_id: str, payload: Dict[str, Any], tts_timestamp: int = None
    ) -> AdvisorySignal:
        """
        Produce a signed advisory signal complying with the canonical schema.

        Args:
            tts_timestamp: Deterministic timestamp from DRV context. If None, uses det_time_now().
        """
        # In a real scenario, this would involve PQC signing.
        # Here we mock the signature.
        mock_signature = f"sig_pqc_{signal_id}_mock"
        timestamp = tts_timestamp if tts_timestamp is not None else det_time_now()

        return AdvisorySignal(
            signal_id=signal_id,
            issuer_id="mock_agent_001",
            payload=payload,
            signature=mock_signature,
            timestamp=timestamp,
        )
