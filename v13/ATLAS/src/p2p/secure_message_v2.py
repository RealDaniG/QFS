from v13.libs.economics.QAmount import QAmount
import json
import base64
import hashlib
import logging
from typing import Dict, Tuple, Optional
logger = logging.getLogger(__name__)

class SecureMessageV2:
    """
    Enhanced secure message format with sequence numbers and timestamps
    to prevent replay attacks and ensure ordering.
    """

    def __init__(self, ciphertext: bytes, nonce: bytes, sequence_num: int, timestamp: QAmount):
        self.ciphertext = ciphertext
        self.nonce = nonce
        self.sequence_num = sequence_num
        self.timestamp = timestamp
        self.message_hash = hashlib.sha256(ciphertext + nonce + sequence_num.to_bytes(8, 'big')).digest()

    def serialize(self) -> bytes:
        """Serialize properly for wire transmission."""
        return json.dumps({'ciphertext': base64.b64encode(self.ciphertext).decode('utf-8'), 'nonce': base64.b64encode(self.nonce).decode('utf-8'), 'seq': self.sequence_num, 'ts': self.timestamp, 'hash': base64.b64encode(self.message_hash).decode('utf-8')}).encode('utf-8')

class MessageSequenceManager:
    """
    Manages peer message sequences to detect gaps and replay attacks.
    """

    def __init__(self):
        self.peer_message_sequences: Dict[str, Tuple[int, int]] = {}

    def get_next_send_seq(self, peer_id: str) -> int:
        """Get the next sequence number for sending to a peer."""
        if peer_id not in self.peer_message_sequences:
            self.peer_message_sequences[peer_id] = (0, 0)
        last_sent, last_recv = self.peer_message_sequences[peer_id]
        new_seq = last_sent + 1
        self.peer_message_sequences[peer_id] = (new_seq, last_recv)
        return new_seq

    def validate_incoming_sequence(self, peer_id: str, seq_num: int) -> bool:
        """
        Validate incoming message sequence number.
        Returns True if valid (new, ordered).
        Returns False if replay or invalid.
        """
        if peer_id not in self.peer_message_sequences:
            self.peer_message_sequences[peer_id] = (0, 0)
        last_sent, last_recv = self.peer_message_sequences[peer_id]
        if seq_num <= last_recv:
            logger.error(f'🚨 Replay attack detected from {peer_id}: seq {seq_num} <= {last_recv}')
            return False
        if seq_num > last_recv + 1:
            logger.warning(f'⚠️ Message gap from {peer_id}: expected {last_recv + 1}, got {seq_num}')
        self.peer_message_sequences[peer_id] = (last_sent, seq_num)
        return True