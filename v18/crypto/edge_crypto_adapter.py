from .ascon_adapter import ascon_adapter, AsconContext, AsconCiphertext, AsconDigest


class EdgeCryptoAdapter:
    """
    Specialized Ascon adapter for edge-focused integrity (Advisory, Telemetry).
    Implements Phase 1 (Infrastructure) and Phase 3 (Edge Integration) readiness.
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.ascon_adapter = ascon_adapter

    def protect_advisory(
        self, advisory_id: str, payload: bytes, key_id: str, seq: int
    ) -> AsconCiphertext:
        """Protects an advisory message with AEAD."""
        context = AsconContext(
            node_id=self.node_id, channel_id="advisory", evidence_seq=seq, key_id=key_id
        )
        key = self._get_edge_key(key_id)
        return ascon_adapter.ascon_aead_encrypt(
            context, payload, advisory_id.encode(), key
        )

    def hash_telemetry(self, packet_id: str, data: bytes) -> AsconDigest:
        """Computes a deterministic digest for telemetry data."""
        context = AsconContext(
            node_id=self.node_id, channel_id="telemetry", evidence_seq=0, key_id="none"
        )
        return ascon_adapter.ascon_hash(context, packet_id.encode() + data)

    def _get_edge_key(self, key_id: str) -> bytes:
        import hashlib

        # Edge keys are derived from node identity
        return hashlib.sha3_256(
            f"edge_master:{self.node_id}:{key_id}".encode()
        ).digest()[:16]


# Global instance for Edge nodes
edge_crypto = EdgeCryptoAdapter(node_id="edge-node-01")
