import logging
import base64
from typing import Dict
from libs.PQC import PQC
from libs.deterministic_helpers import DeterministicID, det_random_bytes

logger = logging.getLogger(__name__)


class PQCServerSession:
    """Manages Server-side KEM keys and ephemeral sessions."""

    def __init__(self):
        # Generate static server KEM key on startup
        with PQC.LogContext() as log:
            self.seed = det_random_bytes(32)
            self.public_key, self.secret_key = PQC.kem_generate_keypair(
                PQC.KYBER1024, self.seed
            )
            logger.info("PQC Secure Chat Server initialized with Kyber1024 keys")

        self.sessions: Dict[str, bytes] = {}  # session_id -> shared_secret

    def create_session(self, ciphertext_b64: str) -> str:
        """Decapsulate and accept session."""
        try:
            ciphertext = base64.b64decode(ciphertext_b64)
            shared_secret = PQC.kem_decapsulate(
                PQC.KYBER1024, self.secret_key, ciphertext
            )
            session_id = str(DeterministicID.next())
            self.sessions[session_id] = shared_secret
            return session_id
        except Exception as e:
            logger.error(f"KEM Decapsulation failed: {e}")
            raise ValueError("Invalid KEM ciphertext")


# Singleton instance
pqc_session_manager = PQCServerSession()
