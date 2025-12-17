import logging
import base64
import uuid
from typing import Dict
from libs.PQC import PQC

logger = logging.getLogger(__name__)


class PQCServerSession:
    """Manages Server-side KEM keys and ephemeral sessions."""

    def __init__(self):
        # Generate static server KEM key on startup
        with PQC.LogContext() as log:
            import os

            self.seed = os.urandom(32)
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
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = shared_secret
            return session_id
        except Exception as e:
            logger.error(f"KEM Decapsulation failed: {e}")
            raise ValueError("Invalid KEM ciphertext")


# Singleton instance
pqc_session_manager = PQCServerSession()
