"""
ProposalEngine.py (v15) - Deterministic Governance State Machine

Enforces strict governance invariants for QFS v15:
- Integer-only thresholds (No floats).
- Canonical serialization (JSON sort_keys=True) for all hashes.
- Proof-of-Execution (PoE) artifact generation.
- Strict isolation of Constitutional vs Mutable parameters.

Invariants:
- GOV-I1: Quorum and Supermajority calculated via integer math.
- GOV-I2: Proposal IDs are content-addressed (SHA3-512).
- GOV-I3: Only whitelisted "Kinds" can be executed.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, field, asdict

# v15 Constants (Integer Percentages)
MIN_QUORUM_PCT = 30
MIN_SUPERMAJORITY_PCT = 66


class ProposalStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"


class ProposalKind(str, Enum):
    PARAMETER_CHANGE = "PARAMETER_CHANGE"
    # Future attributes: EMERGENCY_FREEZE, UPGRADE_CONTRACT


@dataclass
class VoteTally:
    yes: int = 0
    no: int = 0
    abstain: int = 0

    @property
    def total(self) -> int:
        return self.yes + self.no + self.abstain


@dataclass
class Proposal:
    id: str
    kind: ProposalKind
    title: str
    description: str
    proposer: str
    payload_hash: str
    execution_payload: Dict[str, Any]
    status: ProposalStatus = ProposalStatus.DRAFT
    tally: VoteTally = field(default_factory=VoteTally)
    cycle_index: int = 0


class ProposalEngine:
    """
    Deterministic State Machine for v15 Governance.
    """

    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        # Simple Ledger State for validation (Mock for prototype)
        self.total_staked_nod = 10_000  # Example total NOD supply for quorum calcs

    def _canonical_serialize(self, data: Any) -> bytes:
        """Proprietary canonical serialization for v15."""
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def _hash_512(self, data: bytes) -> str:
        """SHA3-512 wrapper for governance IDs."""
        return hashlib.sha3_512(data).hexdigest()

    def create_proposal(
        self,
        kind: ProposalKind,
        title: str,
        description: str,
        proposer: str,
        execution_payload: Dict[str, Any],
        cycle_index: int = 0,
    ) -> str:
        """
        Create a new proposal with deterministic ID generation.
        ID = SHA3-512(Canonical(Payload) + Proposer + Cycle + Kind)
        """
        # 1. Canonical Payload Hash
        payload_bytes = self._canonical_serialize(execution_payload)
        payload_hash = self._hash_512(payload_bytes)

        # 2. Derive Deterministic Proposal ID
        # Structure to hash: [proposer, kind, cycle, payload_hash, title, description]
        # Title/desc included to avoid collision on identical payloads in same cycle/block
        id_seed_struct = [
            proposer,
            kind.value,
            cycle_index,
            payload_hash,
            title,
            description,
        ]
        proposal_id = self._hash_512(self._canonical_serialize(id_seed_struct))

        # 3. Store
        self.proposals[proposal_id] = Proposal(
            id=proposal_id,
            kind=kind,
            title=title,
            description=description,
            proposer=proposer,
            payload_hash=payload_hash,
            execution_payload=execution_payload,
            status=ProposalStatus.ACTIVE,  # Auto-activate for prototype
            cycle_index=cycle_index,
        )

        return proposal_id

    def cast_vote(
        self, proposal_id: str, voter: str, vote_type: str, weight: int
    ) -> bool:
        """
        Cast a weight-based vote.
        Args:
            vote_type: 'YES', 'NO', 'ABSTAIN'
        """
        if proposal_id not in self.proposals:
            return False

        prop = self.proposals[proposal_id]
        if prop.status != ProposalStatus.ACTIVE:
            return False

        # In a real system: Check verify signature, check double vote, check weight
        # Prototype: Just accumulate
        if vote_type == "YES":
            prop.tally.yes += weight
        elif vote_type == "NO":
            prop.tally.no += weight
        elif vote_type == "ABSTAIN":
            prop.tally.abstain += weight
        else:
            return False

        return True

    def try_finalize(self, proposal_id: str) -> Tuple[ProposalStatus, Dict[str, Any]]:
        """
        Attempt to finalize the proposal based on integer thresholds.
        Returns (NewStatus, ProofData).
        """
        if proposal_id not in self.proposals:
            return (ProposalStatus.REJECTED, {})

        prop = self.proposals[proposal_id]

        # Integer Math Thresholds
        total_votes = prop.tally.total

        # 1. Quorum Check
        # participation_pct = (total_votes * 100) // total_staked_nod
        if self.total_staked_nod == 0:
            return (ProposalStatus.REJECTED, {"reason": "Zero Total Stake"})

        participation_pct = (total_votes * 100) // self.total_staked_nod

        if participation_pct < MIN_QUORUM_PCT:
            prop.status = ProposalStatus.REJECTED
            return (
                ProposalStatus.REJECTED,
                {
                    "reason": "Quorum Failed",
                    "participation_pct": participation_pct,
                    "required_pct": MIN_QUORUM_PCT,
                },
            )

        # 2. Supermajority Check
        # yes_ratio_pct = (yes * 100) // (yes + no)
        # Note: Abstains count for quorum but usually excluded from pass/fail ratio,
        # or treated as 'no' depending on governance model.
        # User prompt implies: yes_ratio_pct = prop.votes_yes * 100 // (prop.votes_yes + prop.votes_no)

        deciding_votes = prop.tally.yes + prop.tally.no
        if deciding_votes == 0:
            # All abstained? Fail.
            prop.status = ProposalStatus.REJECTED
            return (ProposalStatus.REJECTED, {"reason": "No Deciding Votes"})

        yes_ratio_pct = (prop.tally.yes * 100) // deciding_votes

        if yes_ratio_pct >= MIN_SUPERMAJORITY_PCT:
            prop.status = ProposalStatus.PASSED
        else:
            prop.status = ProposalStatus.REJECTED

        # 3. Generate Proof Artifact (PoE)
        proof_artifact = {
            "proposal_id": prop.id,
            "final_status": prop.status.value,
            "tally_snapshot": asdict(prop.tally),
            "thresholds": {
                "quorum_pct": MIN_QUORUM_PCT,
                "supermajority_pct": MIN_SUPERMAJORITY_PCT,
            },
            "result_metrics": {
                "participation_pct": participation_pct,
                "yes_ratio_pct": yes_ratio_pct,
            },
            "payload_hash": prop.payload_hash,
        }

        return (prop.status, proof_artifact)

    def execute_proposal(self, proposal_id: str, registry: Any) -> bool:
        """
        Execute a PASSED proposal.
        """
        if proposal_id not in self.proposals:
            return False

        prop = self.proposals[proposal_id]
        if prop.status != ProposalStatus.PASSED:
            return False

        if prop.kind == ProposalKind.PARAMETER_CHANGE:
            key = prop.execution_payload.get("key")
            value_dict = prop.execution_payload.get("value")

            # Simple conversion for prototype
            # Production would use strictly type-checked transformers
            from v13.libs.BigNum128 import BigNum128

            try:
                new_value = (
                    BigNum128.from_int(value_dict)
                    if isinstance(value_dict, int)
                    else BigNum128.from_int(0)
                )

                registry.update_parameter(key, new_value, proposal_id)
                prop.status = ProposalStatus.EXECUTED
                return True
            except Exception as e:
                # Log failure
                print(f"Execution Error: {e}")
                return False

        return False
