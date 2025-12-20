# PR Description: v17 Governance, Bounties, & Social Surface

**Branch:** `feat/v17-governance-bounty-f-layer`
**Status:** ✅ Ready for Review

## Summary

This PR introduces the complete **v17 F-Layer**, providing deterministic, EvidenceBus-driven primitives for Governance, Bounties, and Social Interactions. It includes pure function logic, Pydantic schemas, UI projections, and extensive testing coverage.

## Key Features

### 1. Governance F-Layer (`v17/governance`)

- **Proposals & Voting:** Deterministic proposal creation and vote casting.
- **Outcome Computation:** Pure function `compute_outcome` with configurable quorum/approval thresholds and tie-breaking.
- **EvidenceBus Integration:** All actions emit structured events; state is reconstructed purely from event usage.

### 2. Bounty F-Layer (`v17/bounties`)

- **Lifecycle Management:** Create bounties, submit contributions (with proofs), and finalize rewards.
- **Reward Engine:** Deterministic `compute_rewards` with normalization and caps.
- **Advisory Signals:** Integration for AI agent scoring (non-authoritative).

### 3. Social Surface (`v17/social`)

- **Conversation Binding:** Deterministic Threads linked to Proposals/Bounties via `reference_id`.
- **User Profiles:** `SocialProjection` aggregates a complete user timeline (Votes, Contributions, Threads, Disputes).
- **Disputes:** Formal dispute event flow.

## Hardening & Robustness (CI Fixes)

- **Reward Caps:** `BountyConfig` now supports `max_reward_per_contributor_ratio` to strictly prevent over-allocation.
- **Event Validation:** hardened state reconstruction with `try/except ValidationError` to gracefully handle malformed events.
- **Double-Vote Prevention:** Mandatory state check in `cast_vote` to reject duplicate votes at the F-layer.
- **History Limits:** Increased EvidenceBus fetch limits to 1,000,000 to prevent history truncation.
- **Privacy:** Verified no unredacted wallet logging; compliant with Zero-Sim invariants.

## Testing

- **Unit Tests:**
  - `v17/tests/test_governance_f_layer.py`: ✅ Passed
  - `v17/tests/test_bounties_f_layer.py`: ✅ Passed
  - `v17/tests/test_ui_social.py`: ✅ Passed
- **Integration Tests:**
  - `v17/tests/test_ui_integration.py`: ✅ Passed (Verifies `AdminDashboard` delegation)
- **Zero-Simulation:**
  - Verified no non-deterministic calls (`random`, `time.time()`).
  - Passed `check_zero_sim.py` hooks.

## Documentation

- [x] `V17_IMPLEMENTATION_COMPLETE.md`
- [x] `LAYER_B_IMPLEMENTATION_COMPLETE.md`
- [x] `LAYER_C_IMPLEMENTATION_COMPLETE.md`
