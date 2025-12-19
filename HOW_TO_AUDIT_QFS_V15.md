# How to Audit QFS v15 Autonomous Governance

> **For External Security Reviewers and Auditors**  
> **Version:** v15.0.0  
> **Last Updated:** December 19, 2025

## Overview

This guide explains how to independently verify the QFS v15 Autonomous Governance system through:

1. Local audit suite execution
2. Deterministic replay verification
3. Proof-of-Execution (PoE) artifact validation
4. Hash-chained governance index verification
5. Testnet history verification

## Prerequisites

- Python 3.11+ installed
- Git installed
- 4GB RAM minimum
- Basic understanding of deterministic systems

## Step 1: Clone and Setup

```bash
# Clone repository
git clone https://github.com/RealDaniG/QFS.git
cd QFS

# Checkout v15.0.0
git checkout v15.0.0

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Run Full Audit Suite

```bash
# Execute complete audit suite
python v15/tests/autonomous/test_full_audit_suite.py
```

**Expected Output:**

```
================================================================================
QFS v15 FULL AUDIT SUITE
================================================================================

[AUDIT] Running all test suites...

Ran 23 tests in 0.450s

OK

[AUDIT] Generating audit report...
[AUDIT] Saving results...

[PASS] AUDIT PASSED: All invariants verified
```

**What This Verifies:**

- All 23 governance and operational tests pass
- All 13 invariants are verified
- System is deterministic and replayable

## Step 3: Verify Individual Invariants

### GOV-I1: Integer-Only Voting Thresholds

```bash
python -m pytest v15/atlas/governance/tests/test_proposal_engine.py::TestProposalEngineV15::test_integer_thresholds -v
```

**What to Check:**

- Quorum calculation uses integer math only
- Supermajority calculation uses integer math only
- No floating-point operations in voting logic

### REPLAY-I1: Deterministic Replay

```bash
python -m pytest v15/tests/autonomous/test_governance_replay.py::TestGovernanceReplay::test_bit_for_bit_replay -v
```

**What to Check:**

- Same inputs produce identical outputs
- PoE hashes match exactly
- Zero drift across replays

### AEGIS-G1: Registry-Trigger Coherence

```bash
python -m pytest v15/tests/autonomous/test_stage_6_simulation.py::TestStage6Simulation::test_full_execution_lifecycle -v
```

**What to Check:**

- Registry and Trigger stay synchronized
- AEGIS coherence checks pass
- No desynchronization under load

## Step 4: Deterministic Replay Verification

### Replay a Governance Cycle

```python
# replay_verification.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from v15.atlas.governance import GovernanceParameterRegistry, ProposalEngine
from v13.libs.BigNum128 import BigNum128

def replay_governance_cycle():
    """Replay a governance cycle and verify PoE."""
    
    # Initialize (deterministic seed)
    registry = GovernanceParameterRegistry()
    engine = ProposalEngine(registry)
    
    # Create proposal (deterministic inputs)
    proposal = engine.create_proposal(
        kind="PARAMETER_CHANGE",
        title="Test Proposal",
        description="Deterministic test",
        parameter_key="VIRAL_POOL_CAP",
        new_value=BigNum128(1_500_000_000_000_000_000_000_000_000),
        proposer_wallet="wallet_test"
    )
    
    # Vote
    engine.vote(proposal.proposal_id, "wallet_test", True, stake=1000)
    
    # Execute
    engine.execute_proposal(proposal.proposal_id)
    
    # Get PoE
    poe_hash = engine.get_execution_proof(proposal.proposal_id)
    
    print(f"Proposal ID: {proposal.proposal_id}")
    print(f"PoE Hash: {poe_hash}")
    
    return proposal.proposal_id, poe_hash

# Run twice
print("Run 1:")
id1, hash1 = replay_governance_cycle()

print("\nRun 2:")
id2, hash2 = replay_governance_cycle()

# Verify determinism
assert id1 == id2, "Proposal IDs must match"
assert hash1 == hash2, "PoE hashes must match"

print("\n✅ Deterministic replay verified!")
```

**Run:**

```bash
python replay_verification.py
```

**Expected Output:**

```
Run 1:
Proposal ID: a3f5b2c1d4e6...
PoE Hash: 7f8a9b0c1d2e...

Run 2:
Proposal ID: a3f5b2c1d4e6...
PoE Hash: 7f8a9b0c1d2e...

✅ Deterministic replay verified!
```

## Step 5: PoE Artifact Validation

### Verify PoE Structure

```python
# poe_validation.py
import json

# Load PoE artifact
with open('AUDIT_RESULTS.json', 'r') as f:
    audit = json.load(f)

# Verify structure
required_fields = ['timestamp', 'qfs_version', 'atlas_version', 
                   'total_tests', 'passed_tests', 'invariants']

for field in required_fields:
    assert field in audit, f"Missing required field: {field}"

# Verify invariants
assert len(audit['invariants']) == 13, "Must have 13 invariants"

# Verify all passed
for inv in audit['invariants']:
    assert inv['status'] == 'PASS', f"Invariant {inv['invariant_id']} failed"

print("✅ PoE artifact structure validated!")
```

## Step 6: Testnet History Replay

### Replay Testnet Transactions

```bash
# Get testnet history
curl http://testnet.qfs.example.com:3000/api/v1/governance/history > testnet_history.json

# Replay locally
python tools/replay_testnet_history.py testnet_history.json
```

**What to Verify:**

- Local replay produces same PoE hashes as testnet
- All AEGIS checks pass during replay
- No drift between testnet and local execution

## Step 7: Cross-Platform Verification

### Test on Multiple Platforms

```bash
# Linux
python v15/tests/autonomous/test_full_audit_suite.py

# macOS
python v15/tests/autonomous/test_full_audit_suite.py

# Windows
python v15\tests\autonomous\test_full_audit_suite.py
```

**What to Verify:**

- Same PoE hashes across all platforms
- All tests pass on all platforms
- Zero platform-specific drift

## Step 8: Security Audit Checklist

### Code Review Focus Areas

1. **Immutability Enforcement**
   - File: `v15/atlas/governance/GovernanceParameterRegistry.py`
   - Check: `MUTABLE_KEYS` whitelist enforced
   - Verify: Immutable parameters cannot be changed

2. **Integer-Only Math**
   - File: `v15/atlas/governance/ProposalEngine.py`
   - Check: No floating-point in voting calculations
   - Verify: `check_quorum()` and `check_supermajority()` use integer math

3. **Deterministic Hashing**
   - File: `v15/atlas/governance/ProposalEngine.py`
   - Check: `generate_proposal_id()` uses canonical serialization
   - Verify: SHA3-512 with sorted keys

4. **AEGIS Coherence**
   - File: `v15/atlas/aegis/GovernanceCoherenceCheck.py`
   - Check: Registry-Trigger synchronization
   - Verify: `verify_coherence()` catches desync

### Attack Surface Analysis

**Potential Vulnerabilities to Test:**

1. Proposal ID collision attacks
2. Vote manipulation via stake overflow
3. AEGIS coherence bypass attempts
4. PoE artifact forgery
5. Replay attack vectors

**Recommended Tools:**

- Static analysis: `mypy`, `pylint`
- Fuzzing: `hypothesis`, `atheris`
- Coverage: `pytest-cov`

## Step 9: Performance Benchmarks

```bash
# Run stress test
python v15/tests/autonomous/test_stress_campaign.py

# Check performance
python tools/benchmark_governance.py
```

**Expected Performance:**

- Proposal creation: <10ms
- Vote processing: <5ms
- Execution: <50ms
- AEGIS check: <20ms

## Step 10: Generate Audit Report

```bash
# Run comprehensive audit
python tools/generate_audit_report.py

# Output: external_review/AUDIT_REPORT_[timestamp].pdf
```

## Audit Deliverables

After completing this guide, you should have:

1. ✅ Verified all 23 tests pass
2. ✅ Confirmed all 13 invariants hold
3. ✅ Validated deterministic replay
4. ✅ Verified PoE artifact integrity
5. ✅ Tested cross-platform consistency
6. ✅ Reviewed security-critical code
7. ✅ Analyzed attack surface
8. ✅ Benchmarked performance
9. ✅ Generated audit report

## Questions or Issues?

- **GitHub Issues:** <https://github.com/RealDaniG/QFS/issues>
- **Security:** <security@qfs.example.com>
- **Documentation:** `docs/V15_OVERVIEW.md`

## Audit Report Template

```markdown
# QFS v15 Security Audit Report

**Auditor:** [Your Name/Organization]
**Date:** [Date]
**Version Audited:** v15.0.0
**Commit Hash:** [hash]

## Summary
[Brief overview of findings]

## Test Results
- Total Tests: 23
- Passed: [number]
- Failed: [number]
- Invariants Verified: [number]/13

## Security Findings
[List any vulnerabilities or concerns]

## Recommendations
[Suggested improvements]

## Conclusion
[Overall assessment]
```

---

**Thank you for auditing QFS v15!** Your independent verification helps ensure the security and correctness of the autonomous governance system.
