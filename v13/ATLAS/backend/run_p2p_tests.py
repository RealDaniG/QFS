#!/usr/bin/env python3
"""
One-command P2P test suite launcher
Handles environment setup automatically
"""

import asyncio
import sys
import os

# Inject mock IPFS if not available
try:
    import ipfshttpclient

    # Only use real IPFS if explicitly requested, otherwise default to mock for speed
    USE_REAL_IPFS = os.environ.get("USE_REAL_IPFS", "false").lower() == "true"
except ImportError:
    USE_REAL_IPFS = False

if not USE_REAL_IPFS:
    print("[Test] Using MockIPFSService (Dependency-Free Mode)")
    # We can handle injection by ensuring libraries import from mock if needed
    # But for now, the test_mesh.py explicitly uses get_test_ipfs_service()
    pass
else:
    print("[Test] Using Real IPFS Service (Docker Required)")

# Run the actual test suite
if __name__ == "__main__":
    # Add current dir to path so we can import tests
    sys.path.append(os.path.dirname(__file__))

    from tests.p2p.test_mesh import run_all_tests

    # Run async
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(1)
