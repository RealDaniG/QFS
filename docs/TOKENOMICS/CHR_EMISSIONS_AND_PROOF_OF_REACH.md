# CHR Emissions, Proof-of-Reach, and Governance

## The Logic of QFS Emissions (v13 - v15)

The QFS economic model is activity-based, capped, and now (as of v15 Stage 5) self-amending.

## 1. Proof-of-Reach (Stage 3 Integration)

- **Input**: Normalized viral engagement scores from ATLAS (via `SocialBridge`).
- **Verification**: Cryptographic `EngagementProof` artifacts.
- **Logic**: Score = f(Views, Shares, AuthorRep) [Deterministic].

## 2. The Emission Loop (Stage 4 Economics)

- **Binder**: `ViralRewardBinder` translates Scores → Rewards (CHR).
- **Pro-Rata Distribution**: `UserReward = PoolAmount * (UserScore / TotalScore)`.
- **Hard Caps (`ECON-I1`)**: The total distributed amount *cannot* exceed `VIRAL_POOL_CAP`.
- **Outcome**: High activity days dilute the per-point reward, preventing runaway inflation.

## 3. Governance of Emissions (Stage 5 v15)

The `ProposalEngine` provides a mechanism to adjust economic parameters:

- **Mutable**: `VIRAL_POOL_CAP`, `FLX_REWARD_FRACTION`.
- **Immutable**: `CHR_DAILY_EMISSION_CAP` (The Constitutional Ceiling).

### The Adjustment Cycle

1. **Proposal**: "Increase Viral Pool Cap to 2M CHR."
2. **Vote**: NOD holders approve.
3. **Execute**: v15 Registry updates `VIRAL_POOL_CAP`.
4. **Effect**: The very next batch of rewards uses the new 2M limit.

This ensures the economy can adapt to growth while maintaining mathematical safety guarantees.
