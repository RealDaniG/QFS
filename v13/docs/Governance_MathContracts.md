# Governance Math Contracts (v13.5 / ATLAS v19)

> **Status**: Active
> **Version**: 1.0 (Post-HSMF Alignment)
> **Enforcement**: `ProposalEngine.py`, `VoteEngine.py`, Replay Tests

## Overview

Just as **HSMF** provides deterministic proof-of-evaluation for economic actions, the **Governance Engines** provide deterministic proof-of-consensus for political actions.

Every governance state transition (Proposal Creation, Vote Casting, Tallying) is fully deterministic, replayable, and produces a cryptographic **Proof Object** emitted to the Proof-of-Evidence (PoE) bus.

## 1. Proposal Binding (PROP-Contracts)

A proposal is a binding request to query or mutate the QFS/ATLAS state.

### Invariants

- **PROP-I1 (Hash Binding)**: A proposal's ID MUST be the SHA-256 hash of its immutable definition (title, description, payload, version).
- **PROP-I2 (Payload Integrity)**: The execution payload MUST match the `payload_hash` embedded in the proposal ID.
- **PROP-I3 (Voter Eligibility)**: Only accounts with > 0 reputation (or specific governance tokens) at the proposal's snapshots block can vote.

  }
}

```

## 2. Vote Tallying (VOTE-Contracts)

Votes are weighted signals applied to a proposal.

### Invariants

- **VOTE-I1 (Deterministic Tally)**: Given a set of votes `V` and a weight map `W` (reputation), the tally `T` MUST be identical on every replay.
- **VOTE-I2 (One-Vote-Per-ID)**: A Voter ID can only cast one valid vote per proposal (latest overwrites or rejection).
- **VOTE-I3 (Quorum Check)**: Outcome is strictly a function of `(For, Against, Abstain)` vs `QuorumThreshold`.

### VoteTallyProof Structure

Emitted when a tally is computed (final or intermediate).

```json
{
  "op_name": "vote_tally_proof",
  "proof": {
    "proposal_id": "sha256_hash...",
    "total_votes_cast": "150",
    "total_weight": "5000.000000",
    "outcome": "PASSED",
    "scores": {
        "FOR": "4000.000000",
        "AGAINST": "1000.000000",
        "ABSTAIN": "0.000000"
    },
    "tally_hash": "sha256_of_inputs_and_outputs..."
  }
}
```

## 3. Related Code

- **Proposal Engine**: `v13/policy/governance/ProposalEngine.py`
- **Vote Engine**: `v13/policy/governance/VoteEngine.py`
- **Replay Tests**: `v13/tests/governance/test_governance_replay.py`
