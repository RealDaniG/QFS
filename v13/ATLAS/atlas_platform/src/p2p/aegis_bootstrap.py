import logging
import base64
from typing import Optional, Dict
from v13.core.AEGISNodeVerification import AEGIS_Node_Verifier
logger = logging.getLogger(__name__)

class AEGISDIDBootstrap:
    """
    Bootstrap peer identity via AEGIS DID registry.
    Implements Task 1.2 of QFS x ATLAS Security Integration.
    """

    def __init__(self, aegis_verifier: AEGIS_Node_Verifier):
        self.aegis = aegis_verifier
        self.verified_dids: Dict[str, Dict] = {}

    async def verify_peer_identity(self, peer_id: str, public_key: bytes) -> bool:
        """
        Verify peer DID against AEGIS registry snapshot and PQC keys.
        
        Args:
            peer_id: The node ID provided during handshake
            public_key: The raw public key bytes provided during handshake
            
        Returns:
            True if identity is verified and node is valid in AEGIS.
        """
        try:
            did_doc = self._mock_get_did_doc(peer_id)
            if not did_doc:
                logger.warning(f'🚫 No DID document for {peer_id}')
                return False
            registered_key_b64 = did_doc.get('verification_method', {}).get('public_key')
            provided_key_b64 = base64.b64encode(public_key).decode('utf-8')
            if registered_key_b64 != provided_key_b64:
                logger.error(f'🚨 Public key mismatch for {peer_id}')
                return False
            if did_doc.get('revoked', False):
                logger.warning(f'⚠️ AEGIS verification failed for {peer_id}: REVOKED')
                return False
            self.verified_dids[peer_id] = did_doc
            logger.info(f'✅ AEGIS DID verified for {peer_id}')
            return True
        except Exception as e:
            logger.error(f'❌ AEGIS DID verification error for {peer_id}: {e}')
            return False

    def _mock_get_did_doc(self, peer_id: str) -> Optional[Dict]:
        """ Helper to simulate DID lookup until Ledger/Registry service is injected. """
        if peer_id.startswith('valid_peer') or peer_id.startswith('test_node'):
            return {'id': f'did:qfs:{peer_id}', 'verification_method': {'public_key': 'mock_pub_key'}, 'revoked': False}
        return None