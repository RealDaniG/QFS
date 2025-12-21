# Governance Onboarding Guide (QFS current baseline)

Welcome to the Republic. As a Node Operator (NOD), you are not just a validator; you are a legislator. QFS current baseline introduces a fully autonomous, deterministic governance layer. This guide ensures you can verify and execute your duties safely.

## 1. Verify Your Environment

Before participating, ensure your node is running true current baseline code.

```bash
# Check Release Marker
cat LATEST_RELEASE.txt
# Expected: QFS_VERSION=19.0.0, COMMIT_HASH=REL_v15_0_0
```

## 2. Monitor the Republic

Use the Operator Dashboard to view the state of the union.

```bash
python current baseline/tools/governance_dashboard.py
```

**Key Sections:**

- **System Health (AEGIS)**: Must verify as `✅ PASS`. If this fails, STOP. Your node may be corrupted.
- **Active Parameters**: These are the economic constants currently enforcing price/emission logic.
- **Approved Registry**: Upcoming changes waiting for the next Epoch Tick.

## 3. Verify Proof-of-Execution (PoE)

Every passed proposal generates a cryptographic artifact. You should verify these manually for high-stakes proposals.

1. Locate the Proposal ID from the Dashboard.
2. Find the artifact in your node's ledger storage (mocked at `current baseline/artifacts/` in prototype).
3. Replay the governance cycle locally:

```bash
python current baseline/tests/autonomous/run_autonomous_validation.py
```

This ensures that the "Active Parameters" were derived from a legitimate history of votes, not a backdoor injection.

## 4. Run Health Checks

Periodically run the automated health check to report status to the network.

```bash
python current baseline/ops/ProtocolHealthCheck.py
```

**Metrics:**

- **AEGIS**: Must be Coherent.
- **Drift**: Must be Zero.

## 5. Participation

To propose or vote, reference the [Proposal Engine Spec](../GOVERNANCE/PROPOSAL_ENGINE_SPEC.md). Ensure you calculate 30% Quorum relative to the current Total Stake at the proposal snapshot block.
