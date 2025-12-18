"""
Message Protocol - PQC-Signed Messages for Inter-Module Communication

Zero-Simulation Compliant
"""
from typing import Dict, Any
from pydantic import BaseModel, Field
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from v13.libs.pqc.CanonicalSerializer import CanonicalSerializer
from .pqc_interface import PQCInterface

class SignedMessage(BaseModel):
    """
    PQC-signed message for secure inter-module communication.
    
    All communication between CEE modules MUST use signed messages.
    This ensures:
    - Authenticity: Message came from claimed sender
    - Integrity: Message was not tampered with
    - Non-repudiation: Sender cannot deny sending
    - Auditability: All messages are logged
    """
    sender_qid: str = Field(..., description="Sender's QID")
    recipient_module: str = Field(..., description='Target module name')
    payload: Dict[str, Any] = Field(..., description='Message payload')
    tick: int = Field(..., description='Tick number when sent', ge=0)
    timestamp: int = Field(..., description='Deterministic timestamp', ge=0)
    signature: bytes = Field(..., description='PQC signature')
    public_key: bytes = Field(..., description="Sender's public key")

    class Config:
        frozen = True
        arbitrary_types_allowed = True

    def verify(self, pqc: PQCInterface) -> bool:
        """
        Verify message signature using PQC interface.
        
        Args:
            pqc: PQC implementation to use for verification
            
        Returns:
            True if signature is valid, False otherwise
            
        Deterministic Guarantee:
            Same message + same PQC → same verification result
        """
        canonical_data = {'sender': self.sender_qid, 'recipient': self.recipient_module, 'payload': self.payload, 'tick': self.tick, 'timestamp': self.timestamp}
        canonical_bytes = CanonicalSerializer.serialize_data(canonical_data)
        return pqc.verify(self.public_key, canonical_bytes, self.signature)

    @staticmethod
    def create(sender_qid: str, recipient_module: str, payload: Dict[str, Any], tick: int, timestamp: int, private_key: bytes, public_key: bytes, pqc: PQCInterface) -> 'SignedMessage':
        """
        Create and sign a new message.
        
        Args:
            sender_qid: Sender's QID
            recipient_module: Target module
            payload: Message payload
            tick: Current tick
            timestamp: Deterministic timestamp
            private_key: Sender's private key
            public_key: Sender's public key
            pqc: PQC implementation
            
        Returns:
            Signed message
        """
        canonical_data = {'sender': sender_qid, 'recipient': recipient_module, 'payload': payload, 'tick': tick, 'timestamp': timestamp}
        canonical_bytes = CanonicalSerializer.serialize_data(canonical_data)
        signature = pqc.sign(private_key, canonical_bytes)
        return SignedMessage(sender_qid=sender_qid, recipient_module=recipient_module, payload=payload, tick=tick, timestamp=timestamp, signature=signature, public_key=public_key)
