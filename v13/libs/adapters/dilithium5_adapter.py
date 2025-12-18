"""
Dilithium5 Adapter - Production PQC Implementation

Zero-Simulation Compliant
"""
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from v13.libs.pqc.PQC_Core import Dilithium5Impl
from ..interfaces.pqc_interface import PQCInterface
from typing import Tuple

class Dilithium5Adapter(PQCInterface):
    """
    Production PQC adapter using dilithium-py.
    Wraps Phase-3 PQC_Core Dilithium5Impl for CEE use.
    """

    def keygen(self, seed: bytes) -> Tuple[bytes, bytes]:
        """Generate keypair from 32-byte seed"""
        if len(seed) != 32:
            raise ValueError(f'Seed must be 32 bytes, got {len(seed)}')
        return Dilithium5Impl.keygen(seed)

    def sign(self, private_key: bytes, message: bytes) -> bytes:
        """Sign message with private key"""
        return Dilithium5Impl.sign(private_key, message)

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verify signature"""
        return Dilithium5Impl.verify(public_key, message, signature)
