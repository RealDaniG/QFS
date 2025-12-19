# QFS v15 Governance Dry-Run Scenarios

> **Testnet Validation Scenarios**  
> **Version:** v15.0.0  
> **Purpose:** Verify governance behavior under real-world conditions

## Overview

This directory contains 4 scripted testnet scenarios designed to exercise the full governance system and verify all invariants under realistic conditions.

## Scenarios

### Scenario 1: Change Emission Cap

**File:** `scenario_1_emission_cap.py`  
**Goal:** Increase VIRAL_POOL_CAP from 1B to 1.5B CHR  
**Invariants Tested:** GOV-I1, GOV-I2, GOV-R1, ECON-I1, AEGIS-G1  
**Expected Outcome:** Parameter updated, AEGIS coherent, PoE generated

**Run:**

```bash
python scenarios/scenario_1_emission_cap.py
```

**Expected Output:**

- Proposal created and voted on
- Supermajority achieved (>66%)
- Proposal executed successfully
- Parameter updated: 1B → 1.5B CHR
- AEGIS coherence maintained
- PoE artifact generated

### Scenario 2: Multi-Proposal Stress Test

**File:** `scenario_2_stress_test.py`  
**Goal:** Execute 50 proposals sequentially  
**Invariants Tested:** REPLAY-I1, AEGIS-G1, GOV-R1  
**Expected Outcome:** Zero drift, perfect AEGIS coherence

**Run:**

```bash
python scenarios/scenario_2_stress_test.py
```

**Expected Output:**

- 50 proposals created
- All proposals executed
- Zero drift across all executions
- AEGIS coherence maintained throughout
- Consistent PoE hashes

### Scenario 3: Emergency Rollback

**File:** `scenario_3_rollback.py`  
**Goal:** Rollback to previous parameter snapshot  
**Invariants Tested:** TRIG-I1, AEGIS-G1, GOV-R1  
**Expected Outcome:** Parameters reverted, invariants preserved

**Run:**

```bash
python scenarios/scenario_3_rollback.py
```

**Expected Output:**

- Snapshot created before change
- Parameter changed via proposal
- Rollback executed successfully
- Parameters match snapshot
- AEGIS coherence maintained

### Scenario 4: Reward Multiplier Adjustment

**File:** `scenario_4_reward_multiplier.py`  
**Goal:** Change VIRAL_REWARD_MULTIPLIER from 1.0 to 1.2  
**Invariants Tested:** ECON-I1, AEGIS-G1, GOV-I1  
**Expected Outcome:** Multiplier updated, rewards reflect change

**Run:**

```bash
python scenarios/scenario_4_reward_multiplier.py
```

**Expected Output:**

- Multiplier changed: 1.0 → 1.2
- ViralRewardBinder uses new value
- Rewards calculated correctly
- AEGIS coherence maintained

## Running All Scenarios

```bash
# Run all scenarios sequentially
python scenarios/run_all_scenarios.py
```

**Expected Output:**

```
================================================================================
QFS v15 Testnet Scenarios - Full Suite
================================================================================

[1/4] Running Scenario 1: Change Emission Cap...
✓ Scenario 1 PASSED

[2/4] Running Scenario 2: Multi-Proposal Stress Test...
✓ Scenario 2 PASSED

[3/4] Running Scenario 3: Emergency Rollback...
✓ Scenario 3 PASSED

[4/4] Running Scenario 4: Reward Multiplier Adjustment...
✓ Scenario 4 PASSED

================================================================================
All Scenarios PASSED ✓
================================================================================
```

## Verification

After running scenarios, verify:

1. **PoE Artifacts Generated:**

```bash
ls -la logs/poe_artifacts/
```

2. **AEGIS Coherence:**

```bash
python v15/tools/protocol_health_check.py
```

3. **Dashboard State:**

```bash
python v15/tools/governance_dashboard.py
```

## Success Criteria

Each scenario must:

- ✅ Execute without errors
- ✅ Maintain AEGIS coherence
- ✅ Generate valid PoE artifacts
- ✅ Preserve all invariants
- ✅ Produce deterministic results

## Troubleshooting

**Scenario fails with AEGIS error:**

- Check Registry-Trigger synchronization
- Verify no manual parameter changes
- Run health check

**PoE artifacts not generated:**

- Check `testnet_config.json` has `poe_logging_enabled: true`
- Verify log directory exists
- Check file permissions

**Determinism issues:**

- Ensure same Python version
- Use same input data
- Check for non-deterministic dependencies

## Next Steps

After completing all scenarios:

1. Review PoE artifacts
2. Verify deterministic replay
3. Share results with community
4. Report any issues on GitHub
