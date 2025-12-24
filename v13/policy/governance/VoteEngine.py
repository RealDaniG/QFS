"""
VoteEngine.py - Deterministic Vote Counting and Tallying for QFS v15

This module implements the logic for casting votes and computing tallies
deterministically. It enforces invariants regarding vote weights and
proof generation.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

try:
    from ...libs.CertifiedMath import BigNum128
except ImportError:
    try:
        from v13.libs.CertifiedMath import BigNum128
    except ImportError:
        # Mock for standalone testing if needed, or fail hard in prod
        from decimal import Decimal

        class BigNum128:
            @staticmethod
            def from_int(x):
                return x

            @staticmethod
            def from_string(x):
                return Decimal(x)  # Fallback to Decimal instead of float


class VoteChoice(Enum):
    FOR = "FOR"
    AGAINST = "AGAINST"
    ABSTAIN = "ABSTAIN"


@dataclass
class VoteTallyProof:
    """
    Proof-of-Tally for a governance proposal.
    """

    proposal_id: str
    total_votes: int
    total_weight_str: str
    outcome: str
    scores: Dict[str, str]  # Choice -> Weight String
    tally_hash: str
    version: str = "v1"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "total_votes": self.total_votes,
            "total_weight": self.total_weight_str,
            "outcome": self.outcome,
            "scores": self.scores,
            "tally_hash": self.tally_hash,
            "version": self.version,
        }


class VoteEngine:
    def __init__(self, certified_math=None):
        # proposal_id -> user_id -> {choice, weight}
        self.votes: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # We can accept a CertifiedMath instance if needed for advanced audit logging during add,
        # but for basic accumulation we'll rely on BigNum128 methods.
        self.cm = certified_math

    def _emit_tally_poe(
        self, proof: VoteTallyProof, log_list: Optional[List[Dict[str, Any]]]
    ) -> None:
        if log_list is None:
            return
        log_list.append({"op_name": "vote_tally_proof", "proof": proof.to_dict()})

    def cast_vote(
        self,
        proposal_id: str,
        user_id: str,
        choice: VoteChoice,
        weight: Any,  # BigNum128
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Cast a vote on a proposal. Overwrites previous vote if exists.
        """
        if proposal_id not in self.votes:
            self.votes[proposal_id] = {}

        self.votes[proposal_id][user_id] = {"choice": choice.value, "weight": weight}

        # Log vote cast (lightweight event, not full proof)
        if log_list is not None:
            # Safe conversion to string
            w_str = (
                weight.to_decimal_string()
                if hasattr(weight, "to_decimal_string")
                else str(weight)
            )
            log_list.append(
                {
                    "op_name": "vote_cast",
                    "proposal_id": proposal_id,
                    "user_id": user_id,
                    "choice": choice.value,
                    "weight": w_str,
                }
            )

        return True

    def tally_votes(
        self,
        proposal_id: str,
        quorum: Any,  # BigNum128
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[VoteTallyProof]:
        """
        Compute the tally for a proposal and generate a proof.
        """
        if proposal_id not in self.votes:
            return None

        proposal_votes = self.votes[proposal_id]

        # Helper to getting a zero BigNum safely
        first_weight = next(iter(proposal_votes.values()))["weight"]
        if hasattr(first_weight, "from_int") and callable(
            getattr(first_weight, "from_int")
        ):
            ZERO = first_weight.from_int(0)
        else:
            # Fallback for BigNum128 class method usage or primitive
            try:
                # If weight is an instance, try type(weight).from_int(0)
                ZERO = type(first_weight).from_int(0)
            except:
                ZERO = 0

        scores = {
            VoteChoice.FOR.value: ZERO,
            VoteChoice.AGAINST.value: ZERO,
            VoteChoice.ABSTAIN.value: ZERO,
        }

        total_weight = ZERO
        total_votes = 0

        # Sort by user_id for deterministic iteration
        sorted_users = sorted(proposal_votes.keys())

        for uid in sorted_users:
            v_data = proposal_votes[uid]
            choice = v_data["choice"]
            weight = v_data["weight"]

            if choice in scores:
                if self.cm:
                    scores[choice] = self.cm.add(scores[choice], weight, log_list)
                    total_weight = self.cm.add(total_weight, weight, log_list)
                elif hasattr(weight, "add"):
                    # Method style
                    # Scores MUST be updated by assignment if add returns new obj
                    scores[choice] = scores[choice].add(weight)
                    total_weight = total_weight.add(weight)
                else:
                    # Operator overloading or int
                    scores[choice] += weight
                    total_weight += weight

            total_votes += 1

        # Determine Outcome
        # outcomes: PASSED, REJECTED, FAILED_QUORUM
        outcome = "REJECTED"

        # Check Quorum
        quorum_reached = False
        if self.cm:
            # CertifiedMath.gte args: (a, b, log_list...)
            quorum_reached = self.cm.gte(total_weight, quorum, log_list)
        elif hasattr(total_weight, "gte"):
            quorum_reached = total_weight.gte(quorum)
        else:
            quorum_reached = total_weight >= quorum

        if not quorum_reached:
            outcome = "FAILED_QUORUM"
        else:
            # Majority Check: For > Against
            votes_for = scores[VoteChoice.FOR.value]
            votes_against = scores[VoteChoice.AGAINST.value]

            is_majority = False
            if self.cm:
                is_majority = self.cm.gt(votes_for, votes_against, log_list)
            elif hasattr(votes_for, "gt"):
                is_majority = votes_for.gt(votes_against)
            else:
                is_majority = votes_for > votes_against

            if is_majority:
                outcome = "PASSED"
            else:
                outcome = "REJECTED"

        # Serialize scores
        scores_str = {}
        for k, v in scores.items():
            scores_str[k] = (
                v.to_decimal_string() if hasattr(v, "to_decimal_string") else str(v)
            )

        total_weight_str = (
            total_weight.to_decimal_string()
            if hasattr(total_weight, "to_decimal_string")
            else str(total_weight)
        )

        # Generate Hash
        tally_data = {
            "proposal_id": proposal_id,
            "outcome": outcome,
            "scores": scores_str,
            "total_weight": total_weight_str,
        }
        tally_json = json.dumps(tally_data, sort_keys=True)
        tally_hash = hashlib.sha256(tally_json.encode("utf-8")).hexdigest()

        proof = VoteTallyProof(
            proposal_id=proposal_id,
            total_votes=total_votes,
            total_weight_str=total_weight_str,
            outcome=outcome,
            scores=scores_str,
            tally_hash=tally_hash,
        )

        self._emit_tally_poe(proof, log_list)

        return proof
