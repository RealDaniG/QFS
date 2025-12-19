# Contributors

**Purpose**: Track contributor reputation (ATR) and bounty completion history  
**Status**: Informational (canonical state lives in ledger)  
**Foundation**: v15 Developer Rewards Layer

---

## About ATR (Attention/Reputation)

**ATR** is a **non-transferable reputation metric** that:

- Increases through **merged contributions** and **completed bounties**
- Influences **governance weight** in protocol decisions
- Affects **HSMF engagement weighting** in Living Posts
- Provides **priority** in future proposals and reviews
- **Cannot be transferred, sold, or traded** (utility-only, non-speculative)

### How ATR is Earned

| Activity | ATR Boost | Criteria |
|----------|-----------|----------|
| **Minor Contribution** | +10 ATR | Docs, small fixes, tests |
| **Feature Contribution** | +50 ATR | Modules, services, integrations |
| **Core Contribution** | +100 ATR | Math, Zero-Sim, governance, HSMF |

**Impact Tier Classification**:

- **Minor**: Changes to `docs/`, `tests/`, `scripts/`, small bug fixes
- **Feature**: Changes to `v13/atlas/`, `v13/policy/`, new modules
- **Core**: Changes to `v13/libs/`, `v13/core/`, Zero-Sim, governance

---

## ATR Guarantees

1. **Non-Transferable**: ATR cannot be sent to other wallets
2. **Non-Revocable**: ATR cannot be removed except via explicit slashing (spam/abuse)
3. **Deterministic**: ATR boosts are fixed per impact tier
4. **Replayable**: All ATR changes are logged as `atr_boost_applied` events
5. **Explainable**: Every ATR change links to a specific PR/bounty

---

## Contributor Registry

**Note**: This is an **informational view** only. Canonical ATR state lives in the ledger and `ContributorProfile` records.

| Wallet/DID | Total ATR | Bounties Completed | Impact Tier | Last Contribution |
|------------|-----------|-------------------|-------------|-------------------|
| *No contributors yet* | | | | |

---

## Contribution History

### Example Entry Format

```markdown
#### [Wallet Address / DID]

**Total ATR**: [amount]  
**Bounties Completed**: [count]  
**Highest Impact**: [minor/feature/core]

**Contributions**:
- [YYYY-MM-DD] BOUNTY-YYYY-NNN: [Title] (+[ATR] ATR, [FLX] FLX, [CHR] CHR)
- [YYYY-MM-DD] PR #[number]: [Title] (+[ATR] ATR)
```

---

## ATR Tiers & Roles

While ATR is continuous, these informal tiers help understand contributor standing:

| Tier | ATR Range | Description |
|------|-----------|-------------|
| **Newcomer** | 0-50 | First contributions, learning the protocol |
| **Contributor** | 50-200 | Regular contributions, familiar with codebase |
| **Core Contributor** | 200-500 | Significant features, trusted reviewer |
| **Protocol Steward** | 500+ | Core systems, governance participation |

**Note**: These tiers are **informal** and do not grant special privileges. Governance weight is calculated directly from ATR value.

---

## Governance Weight Calculation

ATR influences governance voting power:

```python
governance_weight = min(1000, ATR / 10)
```

**Example**:

- 100 ATR → 10 governance weight
- 500 ATR → 50 governance weight
- 10,000 ATR → 1000 governance weight (capped)

---

## HSMF Engagement Weighting

ATR affects how engagement is weighted in Living Posts (v15):

```python
reputation_weight = min(1000, ATR / 10)
```

Higher ATR means:

- Your likes/replies carry more weight in post helpfulness scores
- Your engagement is less likely to be filtered as low-quality
- Your posts may receive higher initial coherence scores

---

## How to Become a Contributor

1. **Review Active Bounties**: Check [`BOUNTIES.md`](BOUNTIES.md) for open work
2. **Claim a Bounty**: Stake RES and link your PR
3. **Submit Quality Work**: Meet all acceptance criteria, pass CI
4. **Earn Rewards**: Receive FLX + CHR + ATR boost
5. **Build Reputation**: Continue contributing to increase ATR

---

## Constitutional Constraints

All contributor rewards must:

1. **Be deterministic** (fixed ATR boosts per impact tier)
2. **Be explainable** (link to specific PR/bounty)
3. **Preserve v14 invariants** (no changes to v14 semantics)
4. **Maintain Zero-Sim compliance** (all events replayable)
5. **Respect economic isolation** (ATR is reputation, not currency)

---

## References

- **Bounty System**: [`BOUNTIES.md`](BOUNTIES.md)
- **Developer Rewards Spec**: [`v13/docs/V15_DEVELOPER_REWARDS_SPEC.md`](v13/docs/V15_DEVELOPER_REWARDS_SPEC.md)
- **Contributor Profile Schema**: [`v13/policy/bounties/bounty_schema.py`](v13/policy/bounties/bounty_schema.py)
- **ATR Boost Events**: [`v13/policy/bounties/bounty_events.py`](v13/policy/bounties/bounty_events.py)

---

## Privacy & Data

This file contains **public, non-sensitive information** only:

- Wallet addresses (public on-chain)
- ATR totals (public reputation metric)
- Bounty completion history (public contributions)

**Private information** (email, real names, etc.) is **never** stored here.

---

**Last Updated**: 2025-12-18  
**Status**: Informational Registry  
**Canonical Source**: Ledger + ContributorProfile records
