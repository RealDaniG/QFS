"""
QFS × ATLAS v15 Cryptographic Layer

This module provides the cryptographic primitives for Proof-of-Evidence (PoE) signatures.

**Environment-Aware Design:**
- `ENV=dev` or `ENV=beta` → MOCKQPC (deterministic simulation)
- `ENV=mainnet` → Real PQC (Dilithium via liboqs)

All cryptographic operations MUST route through the adapter layer to ensure
proper environment separation and cost efficiency.
"""

from v15.crypto.mockqpc import mock_sign_poe, mock_verify_poe
from v15.crypto.adapter import sign_poe, verify_poe

__all__ = [
    "mock_sign_poe",
    "mock_verify_poe",
    "sign_poe",
    "verify_poe",
]
