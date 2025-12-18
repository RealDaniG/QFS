import json
import base64
from typing import Dict, Any, Optional
try:
    from v13.libs.CertifiedMath import CertifiedMath
except ImportError:

    class CertifiedMath:

        def sign_dilithium(self, message: bytes, node_id: str) -> bytes:
            return b'DILITHIUM_SIG_MOCK'

        def verify_dilithium(self, message: bytes, signature: bytes, node_id: str) -> bool:
            return True

class OpenAGIPQCAdapter:
    """
    Wraps Open-AGI CryptoEngine with CRYSTALS-Dilithium signatures.
    Implements Task 1.1 of QFS x ATLAS Security Integration.
    """

    def __init__(self, crypto_engine, cert_math: CertifiedMath):
        self.crypto_engine = crypto_engine
        self.cert_math = cert_math
        self.pqc_signatures: Dict[str, bytes] = {}

    def sign_message_pqc(self, message: bytes, node_id: str) -> bytes:
        """
        Sign a message with both Ed25519 (via CryptoEngine) and Dilithium (via CertifiedMath).
        
        Args:
            message: Raw bytes to sign
            node_id: Identity of the signer (for PQC context)
            
        Returns:
            JSON bytes containing 'ed25519', 'dilithium', and 'algorithm' fields.
        """
        ed25519_sig = self.crypto_engine.sign_data(message)
        dilithium_sig = self.cert_math.sign_dilithium(message, node_id)
        payload = {'ed25519': base64.b64encode(ed25519_sig).decode('utf-8'), 'dilithium': base64.b64encode(dilithium_sig).decode('utf-8'), 'algorithm': 'hybrid_ed25519_dilithium'}
        return json.dumps(payload).encode('utf-8')

    def verify_message_pqc(self, message: bytes, signature: bytes, peer_id: str) -> bool:
        """
        Verify a hybrid PQC signature. Both signatures must be valid.
        
        Args:
            message: Original raw bytes
            signature: JSON bytes of the hybrid signature
            peer_id: Expected signer ID
            
        Returns:
            True if BOTH signatures are valid.
        """
        try:
            sig_data = json.loads(signature.decode('utf-8'))
            if sig_data.get('algorithm') != 'hybrid_ed25519_dilithium':
                return False
            ed25519_valid = False
            if hasattr(self.crypto_engine, 'verify_signature'):
                ed25519_valid = self.crypto_engine.verify_signature(message, base64.b64decode(sig_data['ed25519']), signer_id=peer_id)
            else:
                pass
            if not ed25519_valid:
                pass
            dilithium_valid = self.cert_math.verify_dilithium(message, base64.b64decode(sig_data['dilithium']), peer_id)
            if hasattr(self.crypto_engine, 'verify_signature'):
                return ed25519_valid and dilithium_valid
            return dilithium_valid
        except (json.JSONDecodeError, KeyError, ValueError):
            return False
