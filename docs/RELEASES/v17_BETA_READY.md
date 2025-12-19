# QFS × ATLAS v17 Beta - Governance & Bounty F-Layer

> **Status:** Planned  
> **Foundation:** v16 Evergreen Baseline (MOCKQPC-first, Zero-Sim, EvidenceBus-centric)  
> **Target Release:** Q1 2026

---

## Executive Summary

v17 builds on the v16 Evergreen Baseline to add deterministic governance and bounty management layers. All decision-making functions (F-layer) are pure, replayable, and fully integrated with EvidenceBus and agent advisory signals.

## Key Capabilities

### 1. Governance F-Layer ✅ Deterministic

**Proposal Lifecycle:**

- `create_proposal()` - Validates and emits `GOV_PROPOSAL_CREATED` events
- `get_proposal_state()` - Reconstructs state from EvidenceBus events only
- `cast_vote()` - Enforces deterministic voting rules, emits `GOV_VOTE_CAST`
- `compute_outcome()` - Deterministic tallying with threshold evaluation
- `finalize_proposal()` - Emits `GOV_PROPOSAL_FINALIZED` and `GOV_PROPOSAL_EXECUTED`

**Features:**

- Deterministic tie-breaking
- Quorum and threshold enforcement
- Advisory signal integration (agents suggest, F decides)
- Full replay from EvidenceBus event history

### 2. Bounty & Reward F-Layer ✅ Deterministic

**Bounty Lifecycle:**

- `create_bounty()` - Validates and emits `BOUNTY_CREATED` events
- `submit_contribution()` - Tracks contributions via `BOUNTY_CONTRIBUTION_SUBMITTED`
- `compute_rewards()` - Deterministic scoring using PoE + advisory signals
- `finalize_bounty()` - Emits `BOUNTY_REWARD_DECIDED` for settlement

**Features:**

- Multi-contributor reward allocation
- Advisory-enhanced scoring (quality, risk, relevance)
- Deterministic formulas (normalized scores × total reward)
- No direct fund transfers; only PoE events for settlement layers

### 3. Integration Architecture

**EvidenceBus Integration:**

- All governance and bounty events are hash-chained
- Complete audit trails for proposals, votes, executions
- Bounty timelines from creation to reward decisions

**Advisory Layer Integration:**

- Agents provide content scores, recommendations, risk flags
- F-layer consumes advisory signals as non-authoritative input
- Final decisions remain deterministic and replayable

**Admin Dashboard Extensions:**

- Governance timeline viewer (proposal → votes → execution)
- Bounty timeline viewer (bounty → contributions → rewards)
- Advisory overlay showing agent suggestions vs. F decisions

## Implementation Modules

```
v17/
├── governance/
│   ├── f_proposals.py      # Proposal creation and state reconstruction
│   ├── f_voting.py          # Vote casting and validation
│   ├── f_execution.py       # Outcome computation and finalization
│   └── schemas.py           # Pydantic models (Proposal, Vote, ExecutionRecord)
├── bounties/
│   ├── f_bounties.py        # Bounty lifecycle and reward computation
│   └── schemas.py           # Pydantic models (Bounty, Contribution, RewardDecision)
└── tests/
    ├── test_governance_f_layer.py
    └── test_bounties_f_layer.py
```

## Invariants & Guarantees

- ✅ **Deterministic F**: Same event history + config → same outcomes
- ✅ **MOCKQPC-first**: Zero-cost crypto in dev/beta
- ✅ **Zero-Sim**: No randomness, perfect replayability
- ✅ **EvidenceBus-centric**: All state changes via PoE events
- ✅ **Advisory-only agents**: Agents suggest, F decides

## Testing Strategy

**Determinism Tests:**

- Same proposal + votes → same outcome
- Same bounty + contributions + advisory signals → same reward allocation
- Tie-breaking logic is deterministic
- Edge cases: no contributions, equal scores, threshold behavior

**Integration Tests:**

- End-to-end governance flow (create → vote → execute)
- End-to-end bounty flow (create → contribute → reward)
- Advisory signal consumption in F-layer decisions

**Zero-Sim Compliance:**

```bash
ENV=dev MOCKQPC_ENABLED=true CI=true \
pytest && \
python scripts/verify_mockqpc_determinism.py && \
python scripts/check_zero_sim.py --fail-on-critical
```

## Migration Path

**From v16 to v17:**

1. No breaking changes to v16 APIs
2. Governance and bounty F-layers are additive
3. Existing EvidenceBus events remain compatible
4. Advisory layer continues to function unchanged

## Success Metrics

- [ ] 100% deterministic governance outcomes
- [ ] 100% deterministic bounty reward allocation
- [ ] Zero critical Zero-Sim violations
- [ ] Full PoE coverage for all governance and bounty events
- [ ] Advisory signals integrated into F-layer decisions
- [ ] Admin dashboard shows complete governance and bounty timelines

## Next Horizon (v18+)

- Multi-node governance consensus
- Real PQC anchors for mainnet
- External wallet integrations
- Advanced governance (councils, parameter markets)
- Ecosystem incentives for third-party tools

---

**Contract Compliance:** ZERO_SIM_QFS_ATLAS_CONTRACT.md § 2.6, § 4.4  
**Baseline:** v16.0.0-evergreen-baseline  
**Target:** v17.0.0-beta-governance-bounties
