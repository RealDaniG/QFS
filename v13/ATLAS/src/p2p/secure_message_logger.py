from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, det_time_isoformat, qnum
import hashlib
from typing import Dict, Any
try:
    from v13.core.CoherenceLedger import CoherenceLedger, LedgerEntry
except ImportError:

    class LedgerEntry:

        def __init__(self, entry_id, timestamp, entry_type, data, previous_hash, entry_hash, pqc_cid, quantum_metadata):
            self.data = data

    class CoherenceLedger:

        def get_latest_hash(self):
            return 'hash_prev_mock'

        def log_state(self, type, data):
            pass

class SecureMessageLogger:
    """
    Log encrypted messages to QFS ledger for auditability.
    Implements Task 1.3 of QFS x ATLAS Security Integration.
    """

    def __init__(self, ledger: CoherenceLedger):
        self.ledger = ledger

    def log_encrypted_message(self, sender_id: str, recipient_id: str, message_type: str, encrypted_blob: bytes, signature: bytes):
        """
        Log encrypted message with metadata (not plaintext).
        
        Args:
            sender_id: ID of the sender node
            recipient_id: ID of the target node
            message_type: Functional type (e.g., 'CONSENSUS', 'GOSSIP')
            encrypted_blob: The actual encrypted ciphertext bytes
            signature: The raw signature bytes
        """
        timestamp = det_time_now()
        entry_id = f'msg_{sender_id}_{recipient_id}_{int(timestamp * 1000)}'
        blob_hash = hashlib.sha256(encrypted_blob).hexdigest()
        sig_hash = hashlib.sha256(signature).hexdigest()
        data_payload = {'sender_id': sender_id, 'recipient_id': recipient_id, 'message_type': message_type, 'encrypted_blob_hash': blob_hash, 'signature_hash': sig_hash, 'size_bytes': len(encrypted_blob)}
        if hasattr(self.ledger, 'log_state'):
            self.ledger.log_state('secure_message', data_payload)
        else:
            pass
