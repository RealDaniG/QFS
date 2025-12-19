# QFS v15 NOD Operator Guide

> **For Network Operators & Governance Participants**  
> **Version:** v15.0.0  
> **Last Updated:** December 19, 2025

## Overview

This guide explains how to join the QFS v15 testnet as a NOD (Network Operator & Delegate) operator, participate in governance, and monitor system health.

## Prerequisites

- Python 3.11+ installed
- Git installed
- 4GB RAM minimum
- Basic understanding of blockchain governance

## Quick Start

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/RealDaniG/QFS.git
cd QFS

# Checkout v15.0.0
git checkout v15.0.0

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp testnet_env.template .env

# Edit .env with your settings
# Set your wallet address and stake amount
```

### 3. Join Testnet

```bash
# Run testnet initialization
python testnet_init.py

# Expected output:
# ✓ CertifiedMath initialized
# ✓ Registry initialized with 12 parameters
# ✓ ProposalEngine ready
# ✓ GovernanceTrigger initialized
# ✓ AEGIS Status: COHERENT
```

## Governance Participation

### Creating a Proposal

```python
from v15.atlas.governance import GovernanceParameterRegistry, ProposalEngine
from v13.libs.BigNum128 import BigNum128

# Initialize
registry = GovernanceParameterRegistry()
engine = ProposalEngine(registry)

# Create proposal
proposal = engine.create_proposal(
    kind="PARAMETER_CHANGE",
    title="Your Proposal Title",
    description="Detailed description of the change",
    parameter_key="VIRAL_POOL_CAP",  # Parameter to change
    new_value=BigNum128(1_500_000_000_000_000_000_000_000_000),
    proposer_wallet="your_wallet_address"
)

print(f"Proposal created: {proposal.proposal_id}")
```

### Voting on a Proposal

```python
# Vote YES with your stake
engine.vote(
    proposal_id="proposal_id_here",
    voter_wallet="your_wallet_address",
    vote=True,  # True for YES, False for NO
    stake=1000  # Your stake amount
)

print("Vote cast successfully")
```

### Checking Proposal Status

```python
# Check if proposal passed
passed = engine.check_passed("proposal_id_here")

if passed:
    print("Proposal PASSED (>66% supermajority)")
    # Execute if you're authorized
    engine.execute_proposal("proposal_id_here")
else:
    print("Proposal FAILED or still in voting period")
```

## Monitoring & Health Checks

### Run Protocol Health Check

```bash
# Check system health
python v15/tools/protocol_health_check.py

# Expected output:
# ✓ Governance Registry: HEALTHY
# ✓ Governance Trigger: HEALTHY
# ✓ AEGIS Coherence: COHERENT
# ✓ Parameter Integrity: VERIFIED
# ✓ Proposal Engine: OPERATIONAL
# Overall Status: GREEN
```

### View Governance Dashboard

```bash
# View current governance state
python v15/tools/governance_dashboard.py

# Shows:
# - Active parameters
# - Proposal history
# - AEGIS status
# - PoE artifacts
```

### Monitor AEGIS Coherence

```python
from v15.atlas.governance import GovernanceParameterRegistry, GovernanceTrigger
from v15.atlas.aegis import GovernanceCoherenceCheck

# Initialize
registry = GovernanceParameterRegistry()
trigger = GovernanceTrigger(registry, epoch_duration=100)
aegis = GovernanceCoherenceCheck(registry, trigger)

# Check coherence
is_coherent, message = aegis.verify_coherence()

if is_coherent:
    print(f"✓ AEGIS Status: COHERENT - {message}")
else:
    print(f"✗ AEGIS Status: INCOHERENT - {message}")
```

## Understanding Governance Parameters

### Mutable Parameters (Can be changed via governance)

- **VIRAL_POOL_CAP**: Maximum viral reward pool (default: 1B CHR)
- **VIRAL_REWARD_MULTIPLIER**: Reward multiplier (default: 1.0)
- **MIN_PROPOSAL_STAKE**: Minimum stake to create proposal (default: 100 CHR)

### Immutable Parameters (Cannot be changed)

- **QUORUM_THRESHOLD**: Minimum participation (30%)
- **SUPERMAJORITY_THRESHOLD**: Required approval (66%)
- **PROPOSAL_VOTING_PERIOD**: Voting duration (50 blocks)
- **PROPOSAL_EXECUTION_DELAY**: Execution delay (10 blocks)

## Governance Best Practices

### Before Creating a Proposal

1. **Research**: Understand the parameter and its impact
2. **Discuss**: Share your idea in Discord #governance channel
3. **Document**: Write clear title and detailed description
4. **Simulate**: Test locally if possible

### When Voting

1. **Read**: Review proposal title and description
2. **Verify**: Check parameter key and new value
3. **Consider**: Think about economic impact
4. **Vote**: Cast your vote with appropriate stake

### After Execution

1. **Monitor**: Watch for AEGIS coherence
2. **Verify**: Check PoE artifact generated
3. **Report**: Share results in Discord
4. **Document**: Note any issues or observations

## Testnet Scenarios

### Scenario 1: Change Emission Cap

```bash
python scenarios/scenario_1_emission_cap.py
```

**What it does:**

- Increases VIRAL_POOL_CAP from 1B to 1.5B CHR
- Demonstrates full governance cycle
- Verifies AEGIS coherence

### Scenario 2: Multi-Proposal Stress Test

```bash
python scenarios/scenario_2_stress_test.py
```

**What it does:**

- Executes 50 sequential proposals
- Verifies zero drift
- Tests AEGIS under load

### Scenario 3: Emergency Rollback

```bash
python scenarios/scenario_3_rollback.py
```

**What it does:**

- Creates parameter snapshot
- Changes parameter
- Rolls back to snapshot

### Scenario 4: Reward Multiplier Adjustment

```bash
python scenarios/scenario_4_reward_multiplier.py
```

**What it does:**

- Changes VIRAL_REWARD_MULTIPLIER from 1.0 to 1.2
- Demonstrates economic impact
- Verifies reward calculations

## Troubleshooting

### AEGIS Coherence Failure

**Symptom:** `aegis.verify_coherence()` returns False

**Solution:**

1. Check Registry-Trigger synchronization
2. Verify no manual parameter changes
3. Run health check
4. Report issue in Discord

### Proposal Execution Fails

**Symptom:** `execute_proposal()` raises error

**Solution:**

1. Verify proposal passed (>66% supermajority)
2. Check execution delay elapsed
3. Confirm parameter is mutable
4. Check logs for specific error

### Health Check Fails

**Symptom:** Protocol health check returns RED

**Solution:**

1. Check which component failed
2. Review recent governance changes
3. Verify AEGIS coherence
4. Report critical failures immediately

## Discord Integration

### Channels

- **#📡・bot-status**: CI/CD pipeline notifications
- **#governance**: Governance discussions
- **#support**: Technical support
- **#testnet**: Testnet updates

### Notifications

You'll receive Discord notifications for:

- Pipeline success/failure
- Testnet deployments
- Critical health failures
- Governance milestones

## Proof-of-Execution (PoE) Artifacts

### What are PoE Artifacts?

PoE artifacts are cryptographic proofs that governance operations executed correctly.

### Viewing PoE Artifacts

```python
# Get PoE hash for a proposal
poe_hash = engine.get_execution_proof("proposal_id_here")
print(f"PoE Hash: {poe_hash}")
```

### Verifying PoE Artifacts

```bash
# Check PoE artifacts directory
ls -la logs/poe_artifacts/

# Verify artifact integrity
python tools/verify_poe.py <poe_hash>
```

## Security Considerations

### Wallet Security

- **Never share** your wallet private keys
- **Use testnet** wallets only (no real value)
- **Backup** your wallet credentials
- **Rotate** credentials periodically

### Governance Security

- **Verify** proposal details before voting
- **Check** parameter keys match expectations
- **Monitor** AEGIS coherence after changes
- **Report** suspicious proposals immediately

### System Security

- **Run** health checks regularly
- **Monitor** Discord notifications
- **Verify** PoE artifacts
- **Update** to latest version

## Support & Resources

### Documentation

- [RELEASE_NOTES_v15.0.0.md](RELEASE_NOTES_v15.0.0.md) - Release details
- [HOW_TO_AUDIT_QFS_V15.md](HOW_TO_AUDIT_QFS_V15.md) - Auditor guide
- [TESTNET_STATUS.md](TESTNET_STATUS.md) - Testnet status
- [VERIFICATION_STATUS.md](VERIFICATION_STATUS.md) - CI/CD status

### Community

- **Discord**: [Join server](https://discord.gg/qfs)
- **GitHub**: [QFS Repository](https://github.com/RealDaniG/QFS)
- **Issues**: [Report bugs](https://github.com/RealDaniG/QFS/issues)

### Contact

- **Technical Support**: <support@qfs.example.com>
- **Security Issues**: <security@qfs.example.com>
- **Governance Questions**: <governance@qfs.example.com>

## FAQ

**Q: Are testnet tokens worth anything?**
A: No. Testnet tokens have ZERO value and are for testing only.

**Q: Can I lose real money?**
A: No. This is a testnet with fake tokens.

**Q: How often should I run health checks?**
A: At least once per day, or after any governance change.

**Q: What if I find a bug?**
A: Report it on GitHub issues or Discord #support.

**Q: Can I run multiple proposals?**
A: Yes, but ensure each has sufficient stake and community support.

**Q: How do I know if my vote counted?**
A: Check the proposal status and verify your vote in the dashboard.

---

**Welcome to the QFS v15 testnet! Your participation helps make the system more secure and robust.** 🚀
