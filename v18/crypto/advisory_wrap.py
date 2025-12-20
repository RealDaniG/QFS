from typing import Dict, Any, Optional
import json
from .edge_crypto_adapter import edge_crypto


def wrap_advisory_event(
    event: Optional[Dict[str, Any]], key_id: str = "edge_v1", seq: int = 0
) -> Optional[Dict[str, Any]]:
    """
    Wraps an advisory event with Ascon-based integrity digests.
    Implements Phase 3 of the v18.5 Ascon Integration Plan.
    """
    if event is None:
        return None

    payload = event.get("payload", {})
    signal = payload.get("signal", {})
    target_id = signal.get("target_id", "unknown")

    # 1. Deterministic hashing for public integrity
    # Use sort_keys to ensure JSON stringification is deterministic
    signal_bytes = json.dumps(signal, sort_keys=True).encode()
    digest = edge_crypto.hash_telemetry(target_id, signal_bytes)

    # 2. Optional AEAD protection for sensitive advisory metadata
    # (Simulation: We encrypt the 'reasons' list as it might contain PII or sensitive heuristics)
    reasons = signal.get("reasons", [])
    if reasons:
        reasons_json = json.dumps(reasons, sort_keys=True).encode()
        envelope = edge_crypto.protect_advisory(target_id, reasons_json, key_id, seq)
        payload["ascon_protected_reasons"] = envelope.model_dump()
        # In this mode, we could strip the plaintext reasons, but for alpha we keep both for visibility

    payload["ascon_integrity_digest"] = digest.digest_hex
    payload["v18_crypto_layer"] = "ascon-v18.5"

    return event
