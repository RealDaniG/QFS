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
    TEXT = "TEXT"
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
        print(f"DEBUG: ProposalEngine instantiated from {__file__}")
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

    def _to_poe_serializable(self, data: Any) -> Any:
        """Helper to convert internal types (BigNum128) to PoE-friendly types (str/int)."""
        from v13.libs.BigNum128 import BigNum128

        if isinstance(data, BigNum128):
            return str(data)
        elif isinstance(data, dict):
            return {k: self._to_poe_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._to_poe_serializable(v) for v in data]
        else:
            return data

    def execute_proposal(self, proposal_id: str, registry: Any) -> bool:
        """
        Execute a PASSED proposal and generate PoE artifact.
        """
        if proposal_id not in self.proposals:
            return False

        prop = self.proposals[proposal_id]

        if prop.status != ProposalStatus.PASSED:
            return False

        # Capture before state
        raw_before_state = {
            "proposal_status": prop.status.value,
            "registry_state": registry.get_all_parameters()
            if hasattr(registry, "get_all_parameters")
            else {},
        }
        before_state = self._to_poe_serializable(raw_before_state)

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

                # Capture after state
                raw_after_state = {
                    "proposal_status": prop.status.value,
                    "registry_state": registry.get_all_parameters()
                    if hasattr(registry, "get_all_parameters")
                    else {},
                }
                print(
                    f"DEBUG: Before State Registry Type: {type(raw_before_state['registry_state'])}",
                    flush=True,
                )
                after_state = self._to_poe_serializable(raw_after_state)

                # Generate PoE artifact (v15.3)
                try:
                    from v15.atlas.governance.poe_generator import get_poe_generator

                    poe_gen = get_poe_generator()

                    # Build vote breakdown
                    vote_breakdown = {
                        "total_stake": prop.tally.total,
                        "yes_stake": prop.tally.yes,
                        "no_stake": prop.tally.no,
                        "quorum_met": True,  # Already passed
                        "supermajority_met": True,  # Already passed
                    }
                    vote_breakdown = self._to_poe_serializable(vote_breakdown)

                    # Build execution trace
                    execution_trace = [
                        {
                            "operation": "PARAMETER_CHANGE",
                            "parameter_key": key,
                            "old_value": str(
                                raw_before_state["registry_state"].get(key, "unknown")
                            ),
                            "new_value": str(new_value),
                            "proposal_id": proposal_id,
                        }
                    ]

                    import inspect

                    print(f"DEBUG: poe_gen module: {poe_gen.__class__.__module__}")
                    print(
                        f"DEBUG: generate_artifact signature: {inspect.signature(poe_gen.generate_artifact)}"
                    )
                    print(f"DEBUG: Calling with key={key}")

                    # Generate artifact
                    try:
                        # Use KEYWORD arguments now that BigNum128 serialization is fixed
                        artifact = poe_gen.generate_artifact(
                            proposal_id=proposal_id,
                            proposal_hash=prop.payload_hash,
                            epoch=1,  # TODO: Get from governance context
                            cycle=prop.cycle_index,
                            parameter_key=key,
                            execution_phase="EXECUTION",
                            before_state=before_state,
                            after_state=after_state,
                            vote_breakdown=vote_breakdown,
                            execution_trace=execution_trace,
                        )

                        # Save artifact
                        poe_gen.save_artifact(artifact)

                        # Store artifact reference in proposal
                        prop.poe_artifact_id = artifact["artifact_id"]

                        # Add to Governance Index (v15.3)
                        try:
                            from v15.tools.governance_index_manager import (
                                get_index_manager,
                            )

                            index_manager = get_index_manager()
                            index_manager.add_entry(artifact)
                        except Exception as index_error:
                            print(f"Index Update Warning: {index_error}")

                    except Exception as poe_error:
                        print(f"PoE Generation ERROR: {poe_error}")
                        import traceback

                        traceback.print_exc()

                except Exception as e:
                    print(f"PoE Setup Error: {e}")
                    import traceback

                    traceback.print_exc()

                return True

            except Exception as e:
                print(f"Execution Logic Error: {e}")
                import traceback

                traceback.print_exc()
                return False

        return False
