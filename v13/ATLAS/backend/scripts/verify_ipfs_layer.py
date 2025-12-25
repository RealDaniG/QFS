import asyncio
import os
import sys
import shutil
import json
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from lib.trust.envelope import TrustedEnvelope
from lib.ipfs.service import IPFSService
from lib.ipfs.store import IPFSContentStore

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def verify_ipfs_layer():
    logger.info("Locked & Loaded: Verifying ATLAS v19 Phase 2 (IPFS)...")

    # 1. Connect to IPFS
    logger.info("\n[1] Connecting to IPFS Daemon...")
    service = None
    for i in range(5):
        try:
            service = IPFSService()
            # Direct async call
            version = await service.version()
            logger.info(f"IPFS Online! Version: {version['Version']}")
            break
        except Exception as e:
            logger.info(f"Attempt {i + 1}: Failed to connect ({e})")
            if i == 4:
                logger.info("FAIL: Cannot proceed without active IPFS daemon.")
                return
            await asyncio.sleep(2)

    # 2. Store Content
    logger.info("\n[2] Testing IPFSContentStore...")
    store = IPFSContentStore(service)

    envelope = TrustedEnvelope(
        payload_cid="bafy...mockpayload",
        author_address="0x1234567890123456789012345678901234567890",
        signature="0xsignature123",
        content_type="atlas.test.v19",
    )

    try:
        cid = await store.put(envelope)
        logger.info(f"✅ Envelope Stored! CID: {cid}")

        # 3. Retrieve Content
        logger.info("\n[3] Retrieving Content...")
        retrieved = await store.get(cid)

        if retrieved:
            logger.info(
                f"✅ Retrieved: {retrieved.content_type} from {retrieved.author_address}"
            )
            assert retrieved.author_address == envelope.author_address
        else:
            logger.info("❌ Failed to retrieve content.")

    except Exception as e:
        logger.info(f"❌ Storage Operation Failed: {e}")


if __name__ == "__main__":
    asyncio.run(verify_ipfs_layer())
