import asyncio
import os
import sys
import shutil
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from lib.trust.envelope import TrustedEnvelope, EnvelopeVerifier
from lib.trust.storage import LocalContentStore
from lib.trust.identity import PeerIdentity, IdentityVerifier

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def verify_system():
    logger.info("Locked & Loaded: Verifying ATLAS v19 Trust Layer...")

    # 1. Envelope Creation
    logger.info("\n[1] Testing TrustedEnvelope...")
    envelope = TrustedEnvelope(
        payload_cid="bafytest123",
        author_address="0x1234567890123456789012345678901234567890",
        signature="0xsignature123",
        content_type="atlas.post.v1",
        tags=["test", "v19"],
    )
    logger.info(f"Envelope Created: {envelope.generate_hash()}")

    # 2. Verification
    logger.info("\n[2] Testing EnvelopeVerifier...")
    is_valid = EnvelopeVerifier.verify_signature(envelope)
    logger.info(f"Signature Valid? {is_valid}")
    assert is_valid == True

    # 3. Storage
    logger.info("\n[3] Testing LocalContentStore...")
    storage_dir = "./data/v19_test_store"
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)

    store = LocalContentStore(storage_dir)
    ref = await store.put(envelope)
    logger.info(f"Stored Envelope at Ref: {ref}")

    # 4. Retrieval
    logger.info("\n[4] Testing Retrieval...")
    retrieved = await store.get(ref)
    logger.info(f"Retrieved CID: {retrieved.payload_cid}")
    assert retrieved.payload_cid == envelope.payload_cid
    assert retrieved.timestamp == envelope.timestamp

    # 5. Identity
    logger.info("\n[5] Testing PeerIdentity...")
    identity = PeerIdentity(
        peer_id="QmPeerID123",
        wallet_address="0x1234567890123456789012345678901234567890",
        binding_signature="0xbindingsig123",
    )
    is_bound = IdentityVerifier.verify_binding(identity)
    logger.info(f"Identity Bound? {is_bound}")
    assert is_bound == True

    logger.info("\n✅ TRUST MEANING ESTABLISHED. All Systems Go.")


if __name__ == "__main__":
    asyncio.run(verify_system())
