from typing import Optional, Any
from pydantic import BaseModel
import hashlib


class AsconContext(BaseModel):
    """
    Deterministic context for Ascon operations.
    Ensures that nonces and IVs are derived solely from explicitly logged state.
    """

    node_id: str
    channel_id: str  # e.g., "telemetry", "advisory", "cache"
    evidence_seq: int  # or log index / snapshot ID
    key_id: str  # logical key version, not raw key


class AsconCiphertext(BaseModel):
    """Container for AEAD ciphertext and authentication tag."""

    ciphertext_hex: str
    tag_hex: str
    context: AsconContext


class AsconDigest(BaseModel):
    """Container for Ascon-based hash digest."""

    digest_hex: str
    context: AsconContext


class IAsconAdapter:
    """Interface for Ascon-based authenticated encryption and hashing."""

    def __init__(self, emit_callback: Optional[Any] = None):
        self.emit_callback = emit_callback

    def ascon_aead_encrypt(
        self,
        context: AsconContext,
        plaintext: bytes,
        associated_data: bytes,
        key: bytes,
    ) -> AsconCiphertext:
        raise NotImplementedError

    def ascon_aead_decrypt(
        self,
        context: AsconContext,
        ciphertext: AsconCiphertext,
        associated_data: bytes,
        key: bytes,
    ) -> bytes:
        raise NotImplementedError

    def ascon_hash(self, context: AsconContext, message: bytes) -> AsconDigest:
        raise NotImplementedError

    def _log_event(self, event_type: str, context: AsconContext, digest_or_tag: str):
        """Log the crypto operation to EvidenceBus via the callback."""
        if self.emit_callback:
            event = {
                "event_type": f"ASCON_{event_type}",
                "context": context.model_dump(),
                "digest_or_tag": digest_or_tag[:16],  # Truncated for security
                "v18_crypto": "ascon-v18.5",
            }
            self.emit_callback("ASYNC_CRYPTO_EVENT", event)


class MockAsconAdapter(IAsconAdapter):
    """
    A deterministic mock implementation of Ascon using SHA3-256 for simulation.
    Ensures Zero-Simulation compliance by deriving all 'crypto' from the context.
    """

    def _derive_nonce(self, context: AsconContext) -> bytes:
        """Derive a 16-byte nonce deterministically from the context."""
        h = hashlib.sha3_256()
        h.update(context.node_id.encode())
        h.update(context.channel_id.encode())
        h.update(str(context.evidence_seq).encode())
        h.update(context.key_id.encode())
        return h.digest()[:16]

    def ascon_aead_encrypt(
        self,
        context: AsconContext,
        plaintext: bytes,
        associated_data: bytes,
        key: bytes,
    ) -> AsconCiphertext:
        nonce = self._derive_nonce(context)
        # Simulation: XOR plaintext with (key + nonce) hash, Tag is H(plaintext + AD + context)
        # Note: This is NOT real Ascon, but a deterministic simulation for the v18.5 alpha.
        stream_key = hashlib.sha3_256(key + nonce).digest()

        # Simple XOR stream
        cipher_bytes = bytearray()
        for i in range(len(plaintext)):
            cipher_bytes.append(plaintext[i] ^ stream_key[i % len(stream_key)])

        tag_h = hashlib.sha3_256()
        tag_h.update(plaintext)
        tag_h.update(associated_data)
        tag_h.update(context.model_dump_json().encode())
        tag = tag_h.digest()[:16]

        res = AsconCiphertext(
            ciphertext_hex=cipher_bytes.hex(), tag_hex=tag.hex(), context=context
        )
        self._log_event("AEAD_ENCRYPT", context, res.tag_hex)
        return res

    def ascon_aead_decrypt(
        self,
        context: AsconContext,
        ciphertext: AsconCiphertext,
        associated_data: bytes,
        key: bytes,
    ) -> bytes:
        nonce = self._derive_nonce(context)
        stream_key = hashlib.sha3_256(key + nonce).digest()

        cipher_bytes = bytes.fromhex(ciphertext.ciphertext_hex)
        plaintext = bytearray()
        for i in range(len(cipher_bytes)):
            plaintext.append(cipher_bytes[i] ^ stream_key[i % len(stream_key)])

        # Verify tag
        tag_h = hashlib.sha3_256()
        tag_h.update(plaintext)
        tag_h.update(associated_data)
        tag_h.update(context.model_dump_json().encode())
        expected_tag = tag_h.digest()[:16].hex()

        if expected_tag != ciphertext.tag_hex:
            raise ValueError("Ascon AEAD authentication failed - Tag mismatch")

        self._log_event("AEAD_DECRYPT", context, ciphertext.tag_hex)
        return bytes(plaintext)

    def ascon_hash(self, context: AsconContext, message: bytes) -> AsconDigest:
        h = hashlib.sha3_256()
        h.update(context.node_id.encode())
        h.update(context.channel_id.encode())
        h.update(message)
        digest = h.digest().hex()

        res = AsconDigest(digest_hex=digest, context=context)
        self._log_event("HASH", context, digest)
        return res


# Global Instance
ascon_adapter = MockAsconAdapter()
