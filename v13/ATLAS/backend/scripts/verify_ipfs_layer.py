import asyncio
import os
import sys
import shutil
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from lib.trust.envelope import TrustedEnvelope
from lib.ipfs.service import IPFSService
from lib.ipfs.store import IPFSContentStore


async def verify_ipfs_layer():
    print("Locked & Loaded: Verifying ATLAS v19 Phase 2 (IPFS)...")

    # 1. Connect to IPFS
    print("\n[1] Connecting to IPFS Daemon...")
    service = None
    for i in range(5):
        try:
            service = IPFSService()
            # Direct async call
            version = await service.version()
            print(f"IPFS Online! Version: {version['Version']}")
            break
        except Exception as e:
            print(f"Attempt {i + 1}: Failed to connect ({e})")
            if i == 4:
                print("FAIL: Cannot proceed without active IPFS daemon.")
                return
            await asyncio.sleep(2)

    # 2. Store Content
    print("\n[2] Testing IPFSContentStore...")
    store = IPFSContentStore(service)

    envelope = TrustedEnvelope(
        payload_cid="bafy...mockpayload",
        author_address="0x1234567890123456789012345678901234567890",
        signature="0xsignature123",
        content_type="atlas.test.v19",
    )

    try:
        cid = await store.put(envelope)
        print(f"✅ Envelope Stored! CID: {cid}")

        # 3. Retrieve Content
        print("\n[3] Retrieving Content...")
        retrieved = await store.get(cid)

        if retrieved:
            print(
                f"✅ Retrieved: {retrieved.content_type} from {retrieved.author_address}"
            )
            assert retrieved.author_address == envelope.author_address
        else:
            print("❌ Failed to retrieve content.")

    except Exception as e:
        print(f"❌ Storage Operation Failed: {e}")


if __name__ == "__main__":
    asyncio.run(verify_ipfs_layer())
