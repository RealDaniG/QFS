# v15 Governance Parameters

**Version**: v15.0 Protocol Spec  
**Status**: Planned  
**Foundation**: v14.0 Frozen Baseline

This document defines all governable parameters for v15 layers. All changes must go through the **GovernanceStateMachine**.

---

## Living Posts Parameters

| Parameter | Type | Scope | Range | Default | Proposal Type |
|-----------|------|-------|-------|---------|---------------|
| `FLX_POST_POOL[E]` | Integers | Per Epoch | 0 - Hard Cap | 0 | `PoolConfigurationProposal` |
| `SCORE_COEFF_ENGAGEMENT` | Integer | Global | 1 - 1000 | 10 | `ScoringConfigurationProposal` |
| `SCORE_COEFF_COHERENCE` | Integer | Global | 1 - 1000 | 50 | `ScoringConfigurationProposal` |
| `SCORE_COEFF_REPUTATION` | Integer | Global | 1 - 1000 | 20 | `ScoringConfigurationProposal` |
| `TAPER_START_EPOCH` | Integer | Global | 1 - 100 | 10 | `LifecycleConfigurationProposal` |
| `TAPER_FACTOR` | Integer | Global | 1 - 100 (%) | 90 | `LifecycleConfigurationProposal` |
| `ARCHIVE_THRESHOLD` | Integer | Global | 1 - 1000 | 10 | `LifecycleConfigurationProposal` |

---

## Developer Rewards Parameters

| Parameter | Type | Scope | Range | Default | Proposal Type |
|-----------|------|-------|-------|---------|---------------|
| `ATR_BOOST_MINOR` | Integer | Global | 1 - 100 | 10 | `RewardConfigurationProposal` |
| `ATR_BOOST_FEATURE` | Integer | Global | 1 - 500 | 50 | `RewardConfigurationProposal` |
| `ATR_BOOST_CORE` | Integer | Global | 1 - 1000 | 100 | `RewardConfigurationProposal` |
| `TREASURY_REFILL_LIMIT` | Integer | Global | 0 - Max | 10000 | `TreasuryConfigurationProposal` |
| `BOUNTY_APPROVAL_MODE` | Enum | Global | MAINTAINER, GOV | MAINTAINER | `PolicyConfigurationProposal` |

---

## Governance constraints

1. **Activation Epochs**: All parameter changes must specify an activation epoch.
2. **No Retroactive Changes**: Changes apply only to future epochs/events.
3. **Drafting Required**: Proposals must be drafted and open for review before voting.
4. **Log Invariance**: Governance events (`proposal_created`, `proposal_enacted`) are immutable logs.

**Last Updated**: 2025-12-18
