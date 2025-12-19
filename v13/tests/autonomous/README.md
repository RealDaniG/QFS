# Autonomous Constitutional Governance Validation

## Overview

This autonomous validation framework provides self-healing verification of the Tier 1-3 constitutional governance system.

## Phases

### Phase 0: Environment Scan & Baseline

- **File**: `phase_0_scan.py`
- **Purpose**: Verify all critical modules exist and create system checkpoint
- **Checks**:
  - Import statement scanning
  - Module path verification
  - Git hash capture
  - Checkpoint creation

### Phase 2: Constitutional Guard Validation

- **File**: `phase_2_guards.py`
- **Purpose**: Validate all economic guards enforce constitutional bounds
- **Tests**:
  - CHR reward bounds (min/max/daily cap)
  - RES resonance cap (0.5% limit) ✅ **CRITICAL**
  - NOD voting power (25% max) ✅ **CRITICAL**
  - FLX reward fraction bounds
  - PSI delta bounds

## Usage

### Run Full Validation

```bash
cd v13/tests/autonomous
python run_autonomous_validation.py
```

### Run Individual Phases

```bash
# Phase 0 only
python phase_0_scan.py

# Phase 2 only
python phase_2_guards.py
```

## Output

Results are saved to `logs/autonomous/validation_results_TIMESTAMP.json`:

```json
{
  "start_time": "2025-12-19T08:00:00",
  "end_time": "2025-12-19T08:05:00",
  "overall_status": "PASS",
  "phases": {
    "phase_0": {
      "name": "Environment Scan",
      "status": "PASS",
      "timestamp": "2025-12-19T08:01:00"
    },
    "phase_2": {
      "name": "Guard Validation",
      "status": "PASS",
      "timestamp": "2025-12-19T08:04:00"
    }
  }
}
```

## Exit Codes

- `0`: All validations passed
- `1`: One or more validations failed

## Integration with CI/CD

Add to GitHub Actions workflow:

```yaml
- name: Run Autonomous Validation
  run: |
    cd v13/tests/autonomous
    python run_autonomous_validation.py
```

## Checkpoints

System checkpoints are saved to `checkpoints/checkpoint_TIMESTAMP.json` and include:

- All import statements
- Module existence status
- Git commit hash
- Timestamp

Use checkpoints to rollback if validation fails.
