# QFS v15.0.0 - First Testnet Deployment Guide

> **You are the first tester!** 🎉  
> **Release:** v15.0.0 - Autonomous Governance  
> **Status:** Production-Ready - Testnet Deployment

## Quick Start: Become the First Tester

### Step 1: Verify Installation

```bash
# Navigate to QFS directory
cd "d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13"

# Run full audit suite to verify everything is working
python v15/tests/autonomous/test_full_audit_suite.py
```

**Expected Output:**

```
================================================================================
QFS v15 FULL AUDIT SUITE
================================================================================

[AUDIT] Running all test suites...

test_integer_thresholds (v15.atlas.governance.tests.test_proposal_engine.TestProposalEngineV15) ... ok
test_deterministic_id (v15.atlas.governance.tests.test_proposal_engine.TestProposalEngineV15) ... ok
...
[23 more tests]
...

[AUDIT] Generating audit report...
[AUDIT] Saving results...
[AUDIT] Results saved to:
  - AUDIT_RESULTS.json
  - AUDIT_RESULTS_SUMMARY.md

[PASS] AUDIT PASSED: All invariants verified
```

### Step 2: Initialize Your Testnet Governance

Create a new file: `testnet_init.py`

```python
"""
QFS v15.0.0 Testnet Initialization
First Tester: [Your Name]
"""

import sys
from pathlib import Path

# Add v15 to path
sys.path.insert(0, str(Path(__file__).parent))

from v15.atlas.governance import GovernanceParameterRegistry, ProposalEngine, GovernanceTrigger
from v15.atlas.aegis import GovernanceCoherenceCheck
from v13.libs.CertifiedMath import CertifiedMath

def initialize_testnet():
    """Initialize QFS v15 testnet governance."""
    
    print("=" * 80)
    print("QFS v15.0.0 Testnet Initialization")
    print("=" * 80)
    
    # Step 1: Initialize core components
    print("\n[1/5] Initializing CertifiedMath...")
    cm = CertifiedMath()
    print("✓ CertifiedMath initialized")
    
    # Step 2: Create governance registry
    print("\n[2/5] Creating GovernanceParameterRegistry...")
    registry = GovernanceParameterRegistry()
    print(f"✓ Registry initialized with {len(registry.get_all_parameters())} parameters")
    
    # Step 3: Create proposal engine
    print("\n[3/5] Creating ProposalEngine...")
    engine = ProposalEngine(registry)
    print("✓ ProposalEngine ready")
    
    # Step 4: Initialize governance trigger
    print("\n[4/5] Initializing GovernanceTrigger...")
    trigger = GovernanceTrigger(registry, epoch_duration=100)
    print("✓ GovernanceTrigger initialized (epoch duration: 100 blocks)")
    
    # Step 5: Verify AEGIS coherence
    print("\n[5/5] Verifying AEGIS coherence...")
    aegis = GovernanceCoherenceCheck(registry, trigger)
    is_coherent, message = aegis.verify_coherence()
    
    if is_coherent:
        print(f"✓ AEGIS Status: COHERENT - {message}")
    else:
        print(f"✗ AEGIS Status: INCOHERENT - {message}")
        return False
    
    print("\n" + "=" * 80)
    print("Testnet Initialization Complete!")
    print("=" * 80)
    
    # Display current state
    print("\n📊 Current Governance State:")
    print(f"  - Total Parameters: {len(registry.get_all_parameters())}")
    print(f"  - Mutable Parameters: {len(registry.MUTABLE_KEYS)}")
    print(f"  - Immutable Parameters: {len(registry.get_all_parameters()) - len(registry.MUTABLE_KEYS)}")
    print(f"  - Active Proposals: 0")
    print(f"  - Current Epoch: 0")
    print(f"  - AEGIS Status: COHERENT")
    
    return {
        'certified_math': cm,
        'registry': registry,
        'engine': engine,
        'trigger': trigger,
        'aegis': aegis
    }

if __name__ == "__main__":
    components = initialize_testnet()
    
    if components:
        print("\n✅ Ready for first governance proposal!")
        print("\nNext steps:")
        print("  1. Run: python testnet_scenario_1.py")
        print("  2. View dashboard: python v15/tools/governance_dashboard.py")
        print("  3. Check health: python v15/tools/protocol_health_check.py")
    else:
        print("\n❌ Initialization failed - check AEGIS coherence")
        sys.exit(1)
```

### Step 3: Run Initialization

```bash
python testnet_init.py
```

**Expected Output:**

```
================================================================================
QFS v15.0.0 Testnet Initialization
================================================================================

[1/5] Initializing CertifiedMath...
✓ CertifiedMath initialized

[2/5] Creating GovernanceParameterRegistry...
✓ Registry initialized with 12 parameters

[3/5] Creating ProposalEngine...
✓ ProposalEngine ready

[4/5] Initializing GovernanceTrigger...
✓ GovernanceTrigger initialized (epoch duration: 100 blocks)

[5/5] Verifying AEGIS coherence...
✓ AEGIS Status: COHERENT - Registry and Trigger are synchronized

================================================================================
Testnet Initialization Complete!
================================================================================

📊 Current Governance State:
  - Total Parameters: 12
  - Mutable Parameters: 5
  - Immutable Parameters: 7
  - Active Proposals: 0
  - Current Epoch: 0
  - AEGIS Status: COHERENT

✅ Ready for first governance proposal!
```

### Step 4: Create Your First Proposal

Create a new file: `testnet_scenario_1.py`

```python
"""
Testnet Scenario 1: Change Emission Cap
Goal: Increase VIRAL_POOL_CAP from 1B to 1.5B CHR
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from v15.atlas.governance import GovernanceParameterRegistry, ProposalEngine
from v13.libs.BigNum128 import BigNum128

def scenario_1_change_emission_cap():
    """Execute first governance proposal: increase emission cap."""
    
    print("=" * 80)
    print("Testnet Scenario 1: Change Emission Cap")
    print("=" * 80)
    
    # Initialize
    registry = GovernanceParameterRegistry()
    engine = ProposalEngine(registry)
    
    # Your wallet (first tester)
    your_wallet = "wallet_first_tester"
    
    # Step 1: Create proposal
    print("\n[1/4] Creating proposal...")
    proposal = engine.create_proposal(
        kind="PARAMETER_CHANGE",
        title="Increase Viral Pool Cap",
        description="Increase VIRAL_POOL_CAP from 1B to 1.5B CHR to support growing user base",
        parameter_key="VIRAL_POOL_CAP",
        new_value=BigNum128(1_500_000_000_000_000_000_000_000_000),  # 1.5B CHR
        proposer_wallet=your_wallet
    )
    
    print(f"✓ Proposal created!")
    print(f"  - Proposal ID: {proposal.proposal_id}")
    print(f"  - Title: {proposal.title}")
    print(f"  - Parameter: {proposal.parameter_key}")
    print(f"  - New Value: 1,500,000,000 CHR")
    
    # Step 2: Vote (as first tester, you have majority stake)
    print("\n[2/4] Voting on proposal...")
    engine.vote(proposal.proposal_id, your_wallet, True, stake=1000)
    print(f"✓ Vote cast: YES with 1000 stake")
    
    # Step 3: Check if passed
    print("\n[3/4] Checking proposal status...")
    passed = engine.check_passed(proposal.proposal_id)
    
    if passed:
        print("✓ Proposal PASSED (>66% supermajority)")
    else:
        print("✗ Proposal FAILED (need >66% supermajority)")
        return
    
    # Step 4: Execute proposal
    print("\n[4/4] Executing proposal...")
    engine.execute_proposal(proposal.proposal_id)
    print("✓ Proposal executed!")
    
    # Verify change
    new_value = registry.get("VIRAL_POOL_CAP")
    print(f"\n📊 Parameter updated:")
    print(f"  - Old Value: 1,000,000,000 CHR")
    print(f"  - New Value: {int(new_value) // 10**18:,} CHR")
    
    print("\n" + "=" * 80)
    print("Scenario 1 Complete!")
    print("=" * 80)
    
    print("\n✅ First governance proposal executed successfully!")
    print("\nNext steps:")
    print("  1. View dashboard: python v15/tools/governance_dashboard.py")
    print("  2. Check PoE artifact in AUDIT_RESULTS.json")
    print("  3. Run scenario 2: python testnet_scenario_2.py")

if __name__ == "__main__":
    scenario_1_change_emission_cap()
```

### Step 5: Execute First Proposal

```bash
python testnet_scenario_1.py
```

**Expected Output:**

```
================================================================================
Testnet Scenario 1: Change Emission Cap
================================================================================

[1/4] Creating proposal...
✓ Proposal created!
  - Proposal ID: a3f5b2...
  - Title: Increase Viral Pool Cap
  - Parameter: VIRAL_POOL_CAP
  - New Value: 1,500,000,000 CHR

[2/4] Voting on proposal...
✓ Vote cast: YES with 1000 stake

[3/4] Checking proposal status...
✓ Proposal PASSED (>66% supermajority)

[4/4] Executing proposal...
✓ Proposal executed!

📊 Parameter updated:
  - Old Value: 1,000,000,000 CHR
  - New Value: 1,500,000,000 CHR

================================================================================
Scenario 1 Complete!
================================================================================

✅ First governance proposal executed successfully!
```

### Step 6: View Governance Dashboard

```bash
python v15/tools/governance_dashboard.py
```

**Expected Output:**

```
================================================================================
QFS v15 Governance Dashboard
================================================================================

📊 Active Parameters (12):
  - VIRAL_POOL_CAP: 1,500,000,000 CHR [MUTABLE]
  - VIRAL_REWARD_MULTIPLIER: 1.0 [MUTABLE]
  - MIN_PROPOSAL_STAKE: 100 CHR [MUTABLE]
  - QUORUM_THRESHOLD: 30% [IMMUTABLE]
  - SUPERMAJORITY_THRESHOLD: 66% [IMMUTABLE]
  ...

📋 Proposal History (1):
  - a3f5b2... | Increase Viral Pool Cap | EXECUTED

🛡️ AEGIS Status: COHERENT
  - Registry-Trigger sync: ✓
  - Last coherence check: 2025-12-19 13:05:00

📜 Proof-of-Execution Artifacts:
  - Total PoE records: 1
  - Latest: proposal_execution_a3f5b2...
```

### Step 7: Check Protocol Health

```bash
python v15/tools/protocol_health_check.py
```

**Expected Output:**

```
================================================================================
QFS v15 Protocol Health Check
================================================================================

✓ Governance Registry: HEALTHY
✓ Governance Trigger: HEALTHY
✓ AEGIS Coherence: COHERENT
✓ Parameter Integrity: VERIFIED
✓ Proposal Engine: OPERATIONAL

Overall Status: GREEN
Exit Code: 0
```

## Congratulations! 🎉

You are now the **first tester** of QFS v15.0.0 Autonomous Governance!

### What You've Accomplished

1. ✅ Verified v15.0.0 installation (23/23 tests passing)
2. ✅ Initialized testnet governance
3. ✅ Created and executed first governance proposal
4. ✅ Changed a protocol parameter (VIRAL_POOL_CAP)
5. ✅ Verified AEGIS coherence
6. ✅ Generated Proof-of-Execution artifacts

### Next Steps

**More Testnet Scenarios:**

- Scenario 2: Adjust reward multiplier
- Scenario 3: Emergency parameter rollback
- Scenario 4: Multi-proposal stress test

**Share Your Results:**

- Document your testnet experience
- Report any issues on GitHub
- Share PoE artifacts for verification

**Become a NOD Operator:**

- Run continuous health monitoring
- Participate in governance proposals
- Help prepare for mainnet activation

## Support

- **Documentation:** [RELEASE_NOTES_v15.0.0.md](RELEASE_NOTES_v15.0.0.md)
- **Audit Results:** [AUDIT_RESULTS_SUMMARY.md](AUDIT_RESULTS_SUMMARY.md)
- **GitHub Issues:** <https://github.com/RealDaniG/QFS/issues>

---

**You are making history!** This is the first execution of autonomous governance on QFS v15.0.0. 🚀
