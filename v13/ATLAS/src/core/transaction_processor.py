"""
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, det_time_isoformat, qnum
Transaction Processor for ATLAS

This module handles the processing of financial transactions with quantum security.
"""

from typing import Dict, List, Optional, Tuple
from v13.libs.economics.QAmount import QAmount
import hashlib
import json
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """Represents a financial transaction in the ATLAS system."""

    tx_id: str
    sender: str
    receiver: str
    amount: QAmount
    asset: str
    timestamp: str
    signature: Optional[bytes] = None
    status: str = "pending"
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert transaction to dictionary."""
        data = asdict(self)
        if self.signature:
            data["signature"] = self.signature.hex()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Transaction":
        """Create transaction from dictionary."""
        if "signature" in data and isinstance(data["signature"], str):
            data["signature"] = bytes.fromhex(data["signature"])
        return cls(**data)

    def hash(self) -> bytes:
        """Compute the transaction hash."""
        tx_data = self.to_dict()
        tx_data.pop("signature", None)
        tx_data.pop("status", None)
        return hashlib.sha256(json.dumps(tx_data, sort_keys=True).encode()).digest()


class TransactionProcessor:
    """
    Processes and validates financial transactions with quantum security.
    """

    def __init__(self, quantum_engine=None):
        """
        Initialize the transaction processor.

        Args:
            quantum_engine: Instance of QuantumEngine for cryptographic operations
        """
        self.quantum_engine = quantum_engine
        self.pending_transactions: Dict[str, Transaction] = {}
        self.confirmed_transactions: Dict[str, Transaction] = {}
        self.ledger: List[Transaction] = []

    def create_transaction(
        self,
        sender: str,
        receiver: str,
        amount: QAmount,
        asset: str = "QFS",
        metadata: Optional[Dict] = None,
        private_key: Optional[bytes] = None,
    ) -> Transaction:
        """
        Create a new transaction.

        Args:
            sender: Sender's address
            receiver: Recipient's address
            amount: Amount to transfer
            asset: Asset type (default: QFS)
            metadata: Optional transaction metadata
            private_key: Sender's private key for signing

        Returns:
            Transaction: The created transaction
        """
        tx_id = hashlib.sha256(
            f"{sender}{receiver}{amount}{asset}{det_time_isoformat()}".encode()
        ).hexdigest()
        tx = Transaction(
            tx_id=tx_id,
            sender=sender,
            receiver=receiver,
            amount=amount,
            asset=asset,
            timestamp=det_time_isoformat(),
            metadata=metadata or {},
        )
        if private_key and self.quantum_engine:
            tx.signature = self._sign_transaction(tx, private_key)
        return tx

    def _sign_transaction(self, tx: Transaction, private_key: bytes) -> bytes:
        """
        Sign a transaction using the quantum engine.

        Args:
            tx: Transaction to sign
            private_key: Private key for signing

        Returns:
            bytes: Digital signature
        """
        tx_hash = tx.hash()
        if self.quantum_engine:
            return self.quantum_engine._generate_signature(tx_hash, private_key)
        else:
            h = hashlib.shake_256()
            h.update(private_key)
            h.update(tx_hash)
            return h.digest(64)

    def validate_transaction(
        self, tx: Transaction, public_key: Optional[bytes] = None
    ) -> bool:
        """
        Validate a transaction's signature and integrity.

        Args:
            tx: Transaction to validate
            public_key: Optional public key for signature verification

        Returns:
            bool: True if transaction is valid, False otherwise
        """
        if tx.tx_id in self.confirmed_transactions:
            logger.warning(f"Transaction {tx.tx_id} already confirmed")
            return False
        if tx.tx_id in self.pending_transactions:
            logger.warning(f"Transaction {tx.tx_id} already in pending pool")
            return False
        if tx.signature and public_key and self.quantum_engine:
            tx_hash = tx.hash()
            if not self.quantum_engine.verify_quantum_signature(
                tx_hash, tx.signature, public_key
            ):
                logger.error(f"Invalid signature for transaction {tx.tx_id}")
                return False
        if tx.amount <= 0:
            logger.error(f"Invalid amount in transaction {tx.tx_id}")
            return False
        if not tx.sender or not tx.receiver:
            logger.error(f"Missing sender or receiver in transaction {tx.tx_id}")
            return False
        return True

    def add_transaction(
        self, tx: Transaction, public_key: Optional[bytes] = None
    ) -> bool:
        """
        Add a transaction to the pending pool.

        Args:
            tx: Transaction to add
            public_key: Optional public key for validation

        Returns:
            bool: True if transaction was added successfully, False otherwise
        """
        if not self.validate_transaction(tx, public_key):
            return False
        self.pending_transactions[tx.tx_id] = tx
        logger.info(f"Added transaction {tx.tx_id} to pending pool")
        return True

    def process_pending_transactions(self) -> List[Transaction]:
        """
        Process all pending transactions and add them to the ledger.

        Returns:
            List[Transaction]: List of processed transactions
        """
        processed = []
        for tx_id, tx in list(self.pending_transactions.items()):
            tx.status = "confirmed"
            self.confirmed_transactions[tx_id] = tx
            self.ledger.append(tx)
            processed.append(tx)
            del self.pending_transactions[tx_id]
            logger.info(f"Processed transaction {tx_id}")
        return processed

    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """
        Retrieve a transaction by its ID.

        Args:
            tx_id: Transaction ID

        Returns:
            Optional[Transaction]: The transaction if found, None otherwise
        """
        return self.pending_transactions.get(tx_id) or self.confirmed_transactions.get(
            tx_id
        )

    def get_balance(self, address: str, asset: str = "QFS") -> QAmount:
        """
        Calculate the balance for a given address and asset.

        Args:
            address: Address to check balance for
            asset: Asset type (default: QFS)

        Returns:
            QAmount: Current balance
        """
        balance = QAmount(0)
        for tx in sorted(self.ledger):
            if tx.asset != asset:
                continue
            if tx.sender == address:
                balance -= tx.amount
            if tx.receiver == address:
                balance += tx.amount
        return balance
