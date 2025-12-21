# Governance Rollback Playbook (current baseline OPS)

> **Goal**: Deterministically revert a Governance Parameter to a previous state following an erroneous execution.
> **Constraint**: QFS current baseline cannot be "edited" via database access. All rollbacks must occur via **Counter-Proposals**.

## 1. Identify the Incident

Use the Dashboard or Health Check to confirm the bad state.

```bash
python current baseline/tools/governance_dashboard.py
```

*Example: VIRAL_POOL_CAP is accidentally set to 500 (too low).*

## 2. Locate the "Last Known Good" (LKG) State

Recall the value from previous epochs or PoE artifacts.
*Example: LKG Value = 1,000,000 (BigNum128 representation).*

## 3. Create a Counter-Proposal

You must submit a new `PARAMETER_CHANGE` proposal that explicitly sets the value back to the LKG value.

**Script Template:**

```python
from current baseline.atlas.governance.ProposalEngine import ProposalEngine, ProposalKind

engine = ProposalEngine()

payload = {
    "action": "PARAMETER_CHANGE",
    "key": "VIRAL_POOL_CAP",
    "value": 1000000 
}

pid = engine.create_proposal(
    ProposalKind.PARAMETER_CHANGE,
    "ROLLBACK: Restore Viral Pool Cap",
    "Emergency rollback to LKG state.",
    "EmergencyOps",
    payload
)
print(f"Rollback Proposal ID: {pid}")
```

## 4. Emergency Vote

Mobilize the Quorum. Ensure >30% stake participation and >66% Yes votes.

## 5. Execution & Tick

1. **Finalize**: `engine.try_finalize(pid)` -> Generates PoE.
2. **Execute**: `engine.execute_proposal(pid, registry)` -> Updates Registry.
3. **Wait for Epoch**: The new value will activate at the next `GovernanceTrigger.process_tick()`.

## 6. Verify

Run `ProtocolHealthCheck.py` to confirm the warning is resolved and AEGIS is coherent.
