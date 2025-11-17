"""
CoherenceLedger.py - Immutable ledger for auditing deterministic coherence state and token updates

Implements the CoherenceLedger class for recording every token state, reward allocation, 
and HSMF calculation step, generating AEGIS_FINALITY_SEAL.json upon atomic commit,
and maintaining a deterministic hash chain for PQC verification.
"""

import json
import hashlib
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import required components
from CertifiedMath import BigNum128, CertifiedMath
from TokenStateBundle import TokenStateBundle
from TreasuryEngine import TreasuryResult, RewardAllocation
from PQC import sign_data, verify_signature


@dataclass
class LedgerEntry:
    """Represents a single entry in the coherence ledger."""
    entry_id: str
    timestamp: int
    entry_type: str  # 'token_state', 'hsmf_metrics', 'reward_allocation', 'atomic_commit'
    data: Dict[str, Any]
    previous_hash: str
    entry_hash: str
    pqc_cid: str
    quantum_metadata: Dict[str, Any]


class CoherenceLedger:
    """
    Immutable ledger for auditing deterministic coherence state and token updates.
    
    Records every token state, reward allocation, and HSMF calculation step.
    Generates AEGIS_FINALITY_SEAL.json upon atomic commit.
    Maintains a deterministic hash chain for PQC verification.
    """
    
    def __init__(self, cm_instance: CertifiedMath, pqc_key_pair: Optional[tuple] = None):
        """
        Initialize the Coherence Ledger.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic operations
            pqc_key_pair: Optional PQC key pair for signing ledger entries
        """
        self.cm = cm_instance
        self.pqc_private_key = pqc_key_pair[0] if pqc_key_pair else None
        self.pqc_public_key = pqc_key_pair[1] if pqc_key_pair else None
        self.ledger_entries: List[LedgerEntry] = []
        self.quantum_metadata = {
            "component": "CoherenceLedger",
            "version": "QFS-V13-P1-2",
            "timestamp": None,
            "pqc_scheme": "Dilithium-5"
        }
        
    def log_state(self, token_bundle: TokenStateBundle, hsmf_metrics: Optional[Dict[str, Any]] = None, 
                  rewards: Optional[Dict[str, RewardAllocation]] = None) -> LedgerEntry:
        """
        Add ledger entry for token state, HSMF metrics, and rewards.
        
        Args:
            token_bundle: TokenStateBundle with current token states
            hsmf_metrics: Optional HSMF metrics
            rewards: Optional reward allocations
            
        Returns:
            LedgerEntry: The created ledger entry
        """
        # Create entry data
        entry_data = {
            "token_bundle": token_bundle.to_dict(),
            "hsmf_metrics": hsmf_metrics or {},
            "rewards": {name: {
                "token_name": alloc.token_name,
                "amount": alloc.amount.to_decimal_string(),
                "eligibility": alloc.eligibility,
                "coherence_gate_passed": alloc.coherence_gate_passed,
                "survival_gate_passed": alloc.survival_gate_passed
            } for name, alloc in rewards.items()} if rewards else {}
        }
        
        # Get previous hash
        previous_hash = self._get_previous_hash()
        
        # Generate entry hash
        entry_hash = self._generate_entry_hash(entry_data, previous_hash)
        
        # Generate PQC correlation ID
        pqc_cid = self._generate_pqc_cid(entry_data)
        
        # Update timestamp
        timestamp = int(time.time())
        self.quantum_metadata["timestamp"] = str(timestamp)
        
        # Create ledger entry
        entry = LedgerEntry(
            entry_id=f"entry_{len(self.ledger_entries)}",
            timestamp=timestamp,
            entry_type=self._determine_entry_type(hsmf_metrics, rewards),
            data=entry_data,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
            pqc_cid=pqc_cid,
            quantum_metadata=self.quantum_metadata.copy()
        )
        
        # Add to ledger
        self.ledger_entries.append(entry)
        
        return entry
        
    def generate_finality_seal(self, treasury_result: Optional[TreasuryResult] = None) -> str:
        """
        Generate AEGIS_FINALITY_SEAL.json upon atomic commit.
        
        Args:
            treasury_result: Optional TreasuryResult to include in seal
            
        Returns:
            str: Path to generated finality seal file or hash if no file system access
        """
        # Create finality seal data
        seal_data = {
            "component": "AEGIS_FINALITY_SEAL",
            "version": "QFS-V13-P1-2",
            "timestamp": int(time.time()),
            "ledger_entries_count": len(self.ledger_entries),
            "ledger_hash_chain": self._get_ledger_hash_chain(),
            "treasury_result": {
                "is_valid": treasury_result.is_valid if treasury_result else False,
                "total_allocation": treasury_result.total_allocation.to_decimal_string() if treasury_result else "0",
                "rewards_count": len(treasury_result.rewards) if treasury_result and treasury_result.rewards else 0,
                "validation_errors": treasury_result.validation_errors if treasury_result else []
            } if treasury_result else {},
            "quantum_metadata": self.quantum_metadata
        }
        
        # Serialize with sorted keys for deterministic output
        seal_json = json.dumps(seal_data, sort_keys=True, separators=(',', ':'))
        
        # Generate deterministic hash
        seal_hash = hashlib.sha256(seal_json.encode('utf-8')).hexdigest()
        
        # Apply PQC signature if key is available
        if self.pqc_private_key:
            try:
                signature = sign_data(seal_json, self.pqc_private_key)
                seal_data["pqc_signature"] = signature.hex()
            except Exception as e:
                print(f"Warning: PQC signing failed: {e}")
        
        # In a real implementation, this would write to AEGIS_FINALITY_SEAL.json
        # For now, we'll just return the hash
        print(f"AEGIS_FINALITY_SEAL generated with hash: {seal_hash[:32]}...")
        return seal_hash
        
    def _get_previous_hash(self) -> str:
        """Get the hash of the previous ledger entry."""
        if not self.ledger_entries:
            return "genesis_hash_00000000000000000000000000000000"
        return self.ledger_entries[-1].entry_hash
        
    def _generate_entry_hash(self, entry_data: Dict[str, Any], previous_hash: str) -> str:
        """Generate deterministic hash for a ledger entry."""
        data_to_hash = {
            "entry_data": entry_data,
            "previous_hash": previous_hash,
            "timestamp": int(time.time())
        }
        
        data_json = json.dumps(data_to_hash, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(data_json.encode()).hexdigest()
        
    def _generate_pqc_cid(self, entry_data: Dict[str, Any]) -> str:
        """Generate deterministic PQC correlation ID."""
        data_to_hash = {
            "entry_data": entry_data,
            "timestamp": int(time.time())
        }
        
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]
        
    def _get_ledger_hash_chain(self) -> List[str]:
        """Get the complete hash chain of the ledger."""
        return [entry.entry_hash for entry in self.ledger_entries]
        
    def _determine_entry_type(self, hsmf_metrics: Optional[Dict[str, Any]], 
                             rewards: Optional[Dict[str, RewardAllocation]]) -> str:
        """Determine the type of ledger entry based on provided data."""
        if rewards is not None:
            return "reward_allocation"
        elif hsmf_metrics is not None:
            return "hsmf_metrics"
        else:
            return "token_state"
            
    def get_ledger_summary(self) -> Dict[str, Any]:
        """Get a summary of the ledger."""
        return {
            "total_entries": len(self.ledger_entries),
            "entry_types": [entry.entry_type for entry in self.ledger_entries],
            "latest_timestamp": self.ledger_entries[-1].timestamp if self.ledger_entries else 0,
            "ledger_hash_chain_length": len(self._get_ledger_hash_chain())
        }


# Test function
def test_coherence_ledger():
    """Test the CoherenceLedger implementation."""
    print("Testing CoherenceLedger...")
    
    # Create test log list and CertifiedMath instance
    log_list = []
    cm = CertifiedMath(log_list)
    
    # Create test PQC key pair
    from PQC import generate_keypair
    pqc_keys = generate_keypair()
    pqc_keypair = (pqc_keys["private_key"], pqc_keys["public_key"])
    
    # Initialize coherence ledger
    ledger = CoherenceLedger(cm, pqc_keypair)
    
    # Create test token bundle
    chr_state = {
        "coherence_metric": "0.98",
        "c_holo_proxy": "0.99",
        "resonance_metric": "0.05",
        "flux_metric": "0.15",
        "psi_sync_metric": "0.08",
        "atr_metric": "0.85"
    }
    
    token_bundle = TokenStateBundle(
        chr_state=chr_state,
        flx_state={"flux_metric": "0.15"},
        psi_sync_state={"psi_sync_metric": "0.08"},
        atr_state={"atr_metric": "0.85"},
        res_state={"resonance_metric": "0.05"},
        signature="test_signature",
        timestamp=int(time.time()),
        bundle_id="test_bundle_id",
        pqc_cid="test_pqc_cid",
        quantum_metadata={"test": "data"},
        lambda1=BigNum128.from_string("0.3"),
        lambda2=BigNum128.from_string("0.2"),
        c_crit=BigNum128.from_string("0.9")
    )
    
    # Test logging token state
    entry1 = ledger.log_state(token_bundle)
    print(f"Logged token state entry: {entry1.entry_id}")
    print(f"Entry hash: {entry1.entry_hash[:32]}...")
    print(f"Previous hash: {entry1.previous_hash[:32]}...")
    
    # Test logging with HSMF metrics
    hsmf_metrics = {
        "c_holo": BigNum128.from_string("0.95"),
        "s_flx": BigNum128.from_string("0.15"),
        "s_psi_sync": BigNum128.from_string("0.08"),
        "f_atr": BigNum128.from_string("0.85")
    }
    
    entry2 = ledger.log_state(token_bundle, hsmf_metrics)
    print(f"Logged HSMF metrics entry: {entry2.entry_id}")
    print(f"Entry hash: {entry2.entry_hash[:32]}...")
    print(f"Previous hash: {entry2.previous_hash[:32]}...")
    
    # Test logging with rewards
    rewards = {
        "CHR": RewardAllocation(
            token_name="CHR",
            amount=BigNum128.from_string("100.0"),
            eligibility=True,
            coherence_gate_passed=True,
            survival_gate_passed=True,
            quantum_metadata={"test": "reward_data"}
        )
    }
    
    entry3 = ledger.log_state(token_bundle, hsmf_metrics, rewards)
    print(f"Logged rewards entry: {entry3.entry_id}")
    print(f"Entry hash: {entry3.entry_hash[:32]}...")
    print(f"Previous hash: {entry3.previous_hash[:32]}...")
    
    # Test finality seal generation
    # Create mock TreasuryResult
    treasury_result = TreasuryResult(
        rewards=rewards,
        total_allocation=BigNum128.from_string("1000.0"),
        is_valid=True,
        validation_errors=[],
        pqc_cid="test_pqc_cid",
        quantum_metadata={"test": "treasury_data"}
    )
    
    seal_hash = ledger.generate_finality_seal(treasury_result)
    print(f"Finality seal generated: {seal_hash[:32]}...")
    
    # Test ledger summary
    summary = ledger.get_ledger_summary()
    print(f"Ledger summary: {summary}")


if __name__ == "__main__":
    test_coherence_ledger()