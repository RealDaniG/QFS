# Bounties

**Status**: Active (Phase 1 - Manual Processing)  
**Foundation**: v15 Developer Rewards Layer  
**Treasury**: Dev Rewards Treasury (bounded reserves)

---

## Purpose

The QFS × ATLAS bounty system rewards contributors for **deterministic, verifiable work** that advances the protocol while maintaining:

- **Bounded rewards** (no unbounded minting)
- **Deterministic criteria** (fixed rewards, testable acceptance)
- **Explainable outcomes** (bounty ID + commit hash)
- **Zero-Sim compliance** (all events replayable)
- **Constitutional soundness** (non-speculative, utility-only)

---

## How It Works

### 1. Bounty Creation

Maintainers (Phase 1) or governance (Phase 2+) create bounties with:

- **Scope**: Clear description of work
- **Acceptance Criteria**: Deterministic, testable requirements
- **Rewards**: Fixed FLX + CHR amounts
- **RES Stake**: Anti-spam deposit (returned on completion)
- **Impact Tier**: `minor` / `feature` / `core` (determines ATR boost)

### 2. Claim Bounty

Contributors claim by:

- Staking required RES amount
- Linking GitHub PR/commit
- Status: `OPEN` → `CLAIMED`

### 3. Submit Work

Contributors submit by:

- Opening PR with work
- Meeting all acceptance criteria
- Passing CI checks (tests, Zero-Sim, regression)
- Status: `CLAIMED` → `SUBMITTED`

### 4. Verification

Maintainers (Phase 1) or HSMF (Phase 2+) verify:

- CI green (all checks passed)
- Acceptance criteria met
- Zero-Sim compliance (0 violations)
- No v14 semantic changes
- Status: `SUBMITTED` → `VERIFIED`

### 5. Payment

Upon verification:

- FLX + CHR paid from Dev Rewards Treasury
- ATR boost applied (non-transferable reputation)
- RES stake returned
- Status: `VERIFIED` → `PAID`

### Failure Paths

- **Rejected**: Criteria not met, RES returned (good faith) or slashed (spam)
- **Expired**: No submission within timeframe, RES returned

---

## Bounty Lifecycle

```
OPEN → CLAIMED → SUBMITTED → VERIFIED → PAID
         ↓           ↓
      EXPIRED    REJECTED
```

---

## Impact Tiers & ATR Boosts

| Tier | Description | ATR Boost | Examples |
|------|-------------|-----------|----------|
| **minor** | Docs, small fixes, tests | +10 ATR | README updates, test coverage, bug fixes |
| **feature** | Modules, services, features | +50 ATR | New modules, API endpoints, integrations |
| **core** | Math, Zero-Sim, governance | +100 ATR | CertifiedMath, HSMF, state machines |

**ATR (Attention/Reputation)** is non-transferable and influences:

- Governance weight
- HSMF engagement weighting
- Priority in future proposals

---

## Active Bounties

| ID | Title | Scope | Reward | RES Stake | Impact | Status |
|----|-------|-------|--------|-----------|--------|--------|
| *No active bounties* | | | | | | |

---

## Completed Bounties

| ID | Title | Contributor | Reward | ATR Boost | Completed |
|----|-------|-------------|--------|-----------|-----------|
| *No completed bounties yet* | | | | | |

---

## Bounty Template

To create a new bounty, use this template:

```markdown
### BOUNTY-YYYY-NNN: [Title]

**Scope**: [Detailed description of work]

**Acceptance Criteria**:
- [ ] Criterion 1 (deterministic, testable)
- [ ] Criterion 2 (deterministic, testable)
- [ ] All tests pass
- [ ] Zero-Sim compliance (0 violations)
- [ ] Documentation updated

**Rewards**:
- FLX: [amount]
- CHR: [amount]

**RES Stake Required**: [amount]

**Impact Tier**: `minor` / `feature` / `core`

**Status**: OPEN

**Created**: YYYY-MM-DD  
**Created By**: [wallet address]  
**Expires**: YYYY-MM-DD (optional)
```

---

## Constitutional Constraints

All bounties must:

1. **Have deterministic acceptance criteria** (no vague language like "improve" or "optimize")
2. **Preserve v14 invariants** (no semantic or economic changes to v14 baseline)
3. **Maintain Zero-Sim compliance** (all changes must be deterministic and replayable)
4. **Respect economic isolation** (no cross-pool leakage, no minting)
5. **Be explainable** (clear link from work to reward via bounty ID + commit hash)

---

## Treasury Status

**Current Reserves** (as of last update):

- FLX: 10,000 (initial allocation)
- CHR: 5,000 (initial allocation)

**Total Paid**:

- FLX: 0
- CHR: 0

**Depletion Alerts**:

- 🟡 Low: 20% remaining (2,000 FLX / 1,000 CHR)
- 🔴 Critical: 10% remaining (1,000 FLX / 500 CHR)

**Refill Process**: Governance proposal + vote required

---

## Process Documentation

### For Contributors

1. Review active bounties above
2. Claim bounty by staking RES (contact maintainers)
3. Submit work via PR
4. Wait for verification
5. Receive payment + ATR boost

### For Maintainers

1. Create bounty using template
2. Review submissions for acceptance criteria
3. Verify CI status and Zero-Sim compliance
4. Approve payment (Phase 1: manual; Phase 2: automated)
5. Update this file with completion

### For Governance (Phase 2+)

1. Propose new bounties via GovernanceStateMachine
2. Vote on bounty approval
3. HSMF validates completion automatically
4. Payment executes deterministically

---

## References

- **Developer Rewards Spec**: [`v13/docs/V15_DEVELOPER_REWARDS_SPEC.md`](v13/docs/V15_DEVELOPER_REWARDS_SPEC.md)
- **Bounty Schema**: [`v13/policy/bounties/bounty_schema.py`](v13/policy/bounties/bounty_schema.py)
- **Bounty Events**: [`v13/policy/bounties/bounty_events.py`](v13/policy/bounties/bounty_events.py)
- **Dev Rewards Treasury**: [`v13/policy/treasury/dev_rewards_treasury.py`](v13/policy/treasury/dev_rewards_treasury.py)
- **Gap Analysis**: [`v13/docs/DEVELOPER_REWARDS_GAP_ANALYSIS.md`](v13/docs/DEVELOPER_REWARDS_GAP_ANALYSIS.md)

---

**Last Updated**: 2025-12-18  
**Phase**: 1 (Manual Processing)  
**Next**: Phase 2 (Governance Automation)
