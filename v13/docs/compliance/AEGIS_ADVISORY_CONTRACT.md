# AEGIS Advisory Boundaries Contract

**Version:** 1.0  
**Status:** Draft  
**Last Updated:** 2025-12-17  
**Owner:** QFS Security & Architecture Team  
**Extends:** [Zero-Simulation Contract v1.3](../ZERO_SIM_QFS_ATLAS_CONTRACT.md)

---

## Purpose

This contract formally defines the **architectural and security boundaries** between QFS's deterministic core and AEGIS's advisory AI layer. It establishes:

1. **Inviolable constraints** on AI system capabilities
2. **Enforcement mechanisms** to prevent advisory systems from affecting economics
3. **Verification procedures** to audit AEGIS compliance
4. **Failure modes** and degradation policies when boundaries are threatened

**Legal Force:** This is a **constitutional-level** constraint. Violation of this contract is equivalent to violating Zero-Simulation compliance and must trigger immediate quarantine.

---

## Core Principle: Advisory-Only AI

### The Fundamental Rule

> **AEGIS systems SHALL provide explanations, predictions, and recommendations.**  
> **AEGIS systems SHALL NOT make decisions, mutate state, or bypass guards.**

All AI/ML components in the QFS ecosystem are **strictly advisory**. They may:

- ✅ **Observe** ledger state, guard activations, policy configurations
- ✅ **Analyze** patterns in historical data
- ✅ **Recommend** governance actions, parameter changes, learning paths
- ✅ **Explain** why deterministic systems behaved as they did
- ✅ **Predict** likely outcomes of proposed actions (via deterministic simulation)

They must never:

- ❌ **Mutate** token balances, guard thresholds, or policy parameters
- ❌ **Bypass** constitutional guards or authentication
- ❌ **Inject** non-deterministic data into consensus-critical paths
- ❌ **Override** deterministic decisions with AI predictions

---

## Architectural Boundaries

### Boundary 1: Read-Only Access to Economic State

**Contract:**

- All AEGIS services have **read-only database credentials** to RealLedger
- AEGIS API endpoints **cannot call** write methods on Guards, Treasury, or CoherenceLedger
- Database permissions enforced at PostgreSQL role level

**Enforcement:**

```sql
-- AEGIS services use restricted role
CREATE ROLE aegis_readonly WITH LOGIN PASSWORD '...';
GRANT SELECT ON ledger, guards_log, policy_config TO aegis_readonly;
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES FROM aegis_readonly;
```

**Verification:**

- Weekly audit: Check AEGIS service DB user has no write grants
- CI/CD: Test suite attempts AEGIS API → write operation, must fail with `403 Forbidden`

### Boundary 2: No Direct Guard Bypass

**Contract:**

- AEGIS recommendations **pass through** the same guard stack as user actions
- If AEGIS recommends an economic action, that action is submitted as a normal transaction and evaluated by Guards
- AEGIS cannot label transactions as "pre-approved" or "skip guards"

**Enforcement:**

- Guards code review: No `if source == "aegis": skip_check` logic allowed
- All transactions signed with user's PQC key, not AEGIS service key

**Verification:**

- Integration test: AEGIS recommends action that violates guard → system rejects it
- Code audit: Search codebase for AEGIS bypass logic (must be zero occurrences)

### Boundary 3: Advisory Metadata Segregation

**Contract:**

- All AEGIS outputs (explanations, recommendations, risk scores) stored in **separate tables/fields** from deterministic audit trail
- Deterministic replay ignores AEGIS metadata
- AEGIS metadata tagged with `advisory: true` flag in all API responses

**Enforcement:**

```python
# Deterministic audit log
deterministic_log = {
    "operation": "chr_reward",
    "amount": "1000.0",  # BigNum128
    "pqc_cid": "abc123...",
    "hash": "def456..."
}

# AEGIS advisory metadata (separate)
aegis_metadata = {
    "advisory": True,  # REQUIRED flag
    "risk_score": 0.85,
    "explanation": "Guard margin tight, consider...",
    "recommendation": "Reduce reward by 10%",
    "source": "aegis_xai_service"
}
```

**Storage:**

- Deterministic logs: `audit_trail` table (immutable, hash-chained)
- AEGIS metadata: `aegis_advisory` table (mutable, not in replay)

**Verification:**

- Replay test: Deterministic replay produces identical hashes regardless of AEGIS metadata presence/absence
- Schema check: No `aegis_*` fields in core ledger tables

### Boundary 4: Sandbox Isolation

**Contract:**

- Sandbox simulations run in **isolated namespaces** with no network access to RealLedger write endpoints
- Sandbox can read RealLedger snapshots (frozen at sandbox creation time)
- Sandbox state is **ephemeral** and destroyed after execution
- Sandbox results **never auto-merge** into RealLedger

**Enforcement:**

```yaml
# Docker/K8s sandbox isolation
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    readOnlyRootFilesystem: true
  containers:
  - name: sandbox
    image: qfs-sandbox:latest
    resources:
      limits:
        cpu: "2"
        memory: "4Gi"
        ephemeral-storage: "10Gi"
    env:
    - name: LEDGER_MODE
      value: "SNAPSHOT_READONLY"
    - name: NETWORK_MODE
      value: "ISOLATED"
```

**Verification:**

- Network test: Sandbox attempts HTTP call to RealLedger write endpoint → connection refused
- State test: Run sandbox → destroy namespace → assert no RealLedger mutations
- Replay test: Sandbox produces deterministic hash on identical inputs

### Boundary 5: ML Inference Isolation

**Contract:**

- ML model inference (pattern detection, XAI feature importance) runs in **advisory layer only**
- ML outputs **cannot be directly** written to ledger or guards
- ML models are **versioned** and their outputs logged for auditability

**Enforcement:**

- ML serving endpoint (TorchServe) has no access to write-enabled ledger credentials
- All ML predictions logged with model version, input hash, inference timestamp

**Logging Example:**

```json
{
  "ml_prediction": {
    "model_id": "pattern_detector_v2.1",
    "input_hash": "abc123...",
    "prediction": {
      "pattern_id": "EA-3",
      "confidence": 0.87
    },
    "advisory": true,
    "timestamp": 1702835623,
    "inference_time_ms": 45
  }
}
```

**Verification:**

- Code audit: No ML predictions in `if` statements controlling economic logic
- Test: Corrupt ML model output → verify system degrades to rule-based heuristics, not errors

---

## Failure Modes & Degradation Policies

### Failure Mode 1: AEGIS Service Offline

**Trigger:** AEGIS telemetry service unreachable for >5 minutes

**Degradation Policy:**

- Switch to **cached telemetry snapshots** (already implemented in `aegis_api.py`)
- Governance consequence maps use **deterministic simulation only** (no live risk scores)
- Pattern analysis falls back to **rule-based heuristics**
- XAI service uses **template-based explanations** (no ML-generated narratives)

**User Impact:**

- Reduced recommendation quality
- Stale risk scores (based on last cached snapshot)
- No real-time anomaly detection

**Allowed Behavior:**

- ✅ Governance UX still functional (consequence maps work)
- ✅ Sandbox simulations still deterministic
- ✅ All guards still enforce (no economic impact)

**Forbidden Behavior:**

- ❌ Approximate/interpolate missing telemetry data
- ❌ Use fallback "default" risk scores that affect guard behavior
- ❌ Block governance actions due to missing AEGIS data

**Logging:**

```json
{
  "event": "aegis_offline_policy_triggered",
  "severity": "CRITICAL",
  "policy": "freeze_realtime_telemetry_use_cache",
  "timestamp": 1702835623,
  "last_successful_snapshot": "block_12345"
}
```

**Recovery:**

- When AEGIS service returns, verify snapshot hash continuity
- Incrementally update cache with new snapshots
- Resume real-time features only after hash verification passes

### Failure Mode 2: AEGIS Recommends Guard-Violating Action

**Trigger:** User accepts AEGIS recommendation, submits action, guard rejects

**Expected Flow (Normal):**

1. AEGIS recommends: "Increase CHR reward to 1500"
2. User submits transaction
3. Guard evaluates: "Daily limit exceeded"
4. Guard **rejects** (AEGIS recommendation overruled)
5. User sees: "Action blocked by EconomicsGuard (daily limit)"

**Policy:**

- This is **expected behavior** - AEGIS is advisory, not authoritative
- Log as `aegis_recommendation_overruled` (info level, not error)
- Use for ML feedback loop: "This recommendation pattern leads to guard failures"

**Forbidden Response:**

- ❌ Bypass guard because "AEGIS recommended it"
- ❌ Treat as system error (it's working as designed)

### Failure Mode 3: Sandbox Escape Attempt

**Trigger:** Sandbox process attempts unauthorized access to RealLedger write endpoints or filesystem escape

**Immediate Response:**

1. **Terminate sandbox** namespace immediately (SIGKILL)
2. **Quarantine** sandbox template + user parameters
3. **Alert** security team (PagerDuty/Slack)
4. **Log** full syscall trace for forensics

**Investigation:**

- Was this malicious user input or software bug?
- Does sandbox isolation need hardening?
- Update security threat model

**Recovery:**

- Fix sandbox isolation vulnerability
- Re-audit all sandbox code for escape vectors
- Resume sandbox service only after security review

### Failure Mode 4: Boundary Violation Detected

**Trigger:** Audit finds AEGIS metadata in deterministic replay path or AEGIS service with write access

**Severity:** **CRITICAL** - Constitutional violation

**Immediate Response:**

1. **Halt** AEGIS service deployment
2. **Trigger CIR-302 quarantine** if economic state affected
3. **Revert** to last known-good configuration
4. **Audit** all transactions since violation introduced

**Root Cause Analysis:**

- How did boundary violation occur? (Code bug, config error, malicious PR?)
- Was economic state corrupted?
- Can we replay from known-good state?

---

## Verification Procedures

### Daily Automated Checks

**Script:** `v13/scripts/verify_aegis_boundaries.py`

```python
def verify_aegis_boundaries():
    checks = []
    
    # Check 1: Database permissions
    aegis_role = get_db_role("aegis_readonly")
    assert not aegis_role.has_write_permissions(), "AEGIS has write access!"
    checks.append("db_permissions_ok")
    
    # Check 2: No AEGIS metadata in deterministic logs
    recent_logs = get_audit_trail(last_hours=24)
    for log in recent_logs:
        assert "aegis_" not in log.keys(), f"AEGIS field in log: {log}"
    checks.append("log_segregation_ok")
    
    # Check 3: Sandbox isolation
    test_sandbox = create_sandbox()
    try:
        test_sandbox.attempt_write_to_real_ledger()
        assert False, "Sandbox write should fail!"
    except PermissionError:
        checks.append("sandbox_isolation_ok")
    
    # Check 4: Guard bypass attempt
    aegis_tx = create_transaction(source="aegis_service", bypass_guards=True)
    result = submit_transaction(aegis_tx)
    assert result.status == "REJECTED", "AEGIS bypass succeeded!"
    checks.append("guard_enforcement_ok")
    
    return all(checks)
```

**Run:** Daily via CI/CD, alerts on failure

### Weekly Security Audit

**Performed by:** Security team or automated scanner

**Checklist:**

- [ ] Review AEGIS service database credentials (still read-only?)
- [ ] Scan codebase for `aegis` + `bypass` co-occurrence
- [ ] Check sandbox namespace count (any orphaned namespaces?)
- [ ] Review AEGIS recommendation acceptance rate (unusually high = potential bypass?)
- [ ] Verify ML model versions (no unauthorized updates?)

### Monthly Boundary Compliance Report

**Generated by:** Tech lead

**Includes:**

- Number of AEGIS recommendations overruled by guards (should be >0, proof of independence)
- Sandbox execution failures (high rate = isolation issues)
- AEGIS offline incidents and degradation behavior
- Any boundary violation incidents (should be 0)

**Distribution:** Security team, exec team, auditors

---

## Compliance with Existing Contracts

### Zero-Simulation Contract Alignment

| Zero-Sim Requirement | AEGIS Compliance |
|----------------------|------------------|
| No randomness in consensus | ✅ ML inference is advisory only, not in consensus path |
| No wall-clock time | ✅ AEGIS uses ledger timestamps from DRV_Packets |
| No floating-point economics | ✅ AEGIS cannot write to economic state |
| Deterministic replay | ✅ AEGIS metadata excluded from replay |
| PQC signatures required | ✅ AEGIS recommendations signed with user keys when submitted |

### Constitutional Guards Alignment

**AEGIS relationship to Guards:**

- **Observation:** AEGIS observes guard activations (via `AEGISGuard.observe_event()`)
- **Explanation:** AEGIS explains why guards fired
- **Prediction:** AEGIS predicts which guards will fire for proposed actions
- **Enforcement:** Guards are the **sole authority** on economic constraints

**Guard Independence:**

- Guards **never query** AEGIS for decisions
- Guards evaluate based on ledger state + policy parameters only
- AEGIS can recommend guard threshold changes, but those changes go through governance (voted on, not auto-applied)

---

## Implementation Checklist

Before deploying any AEGIS UX feature:

- [ ] Code review confirms read-only database access
- [ ] Integration test: AEGIS cannot bypass guards
- [ ] Deterministic replay test passes (ignores AEGIS metadata)
- [ ] Sandbox isolation verified (network + filesystem)
- [ ] ML model outputs logged with version + advisory flag
- [ ] Offline degradation mode tested
- [ ] Security review approved
- [ ] Documentation updated (this contract + feature spec)

---

## Governance & Amendment Process

**Amendment Authority:** Requires unanimous agreement from:

- QFS tech lead
- Security team lead
- At least 2 constitutional guard maintainers

**Amendment Process:**

1. Proposal submitted via governance portal
2. Consequence map analysis (using AEGIS UX once available)
3. 7-day review period
4. Security audit of proposed change
5. Vote by authority group
6. If approved: Update contract, increment version, redeploy with new constraints

**Immutable Clauses (Cannot Be Amended):**

- Core Principle: "Advisory-Only AI" (Boundary 1)
- Sandbox mutations never merge to RealLedger (Boundary 4)

---

## References

- [AEGIS UX Architecture](AEGIS_UX_ARCHITECTURE.md) - System design
- [Zero-Simulation Contract v1.3](../ZERO_SIM_QFS_ATLAS_CONTRACT.md) - Parent contract
- [Constitutional Guards Spec](../governance/) - Guard enforcement
- [CIR-302 Quarantine Spec](../../handlers/CIR302_Handler.py) - Failure handling

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-17 | QFS Security Team | Initial contract based on Zero-Sim v1.3 |

---

**Next Document:** [Governance Consequence Map Specification](../governance/CONSEQUENCE_MAP_SPEC.md) (P0-3)
