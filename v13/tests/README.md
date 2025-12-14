# QFS V13 Test Suite Documentation

## Overview

This directory contains the comprehensive test suite for QFS V13, including all V13.6 constitutional guard verification tests and PQC standardization tests.

## V13.6 Test Suites

### 1. DeterministicReplayTest.py
Validates NOD-I4 deterministic replay with AEGIS snapshots.

**Purpose:** Ensure bit-for-bit identical results across runs with identical inputs.

**Execution:**
```bash
cd /path/to/qfs-v13
python -m tests.v13_6.DeterministicReplayTest
```

**Evidence Artifact:** `evidence/v13_6/nod_replay_determinism.json`

### 2. BoundaryConditionTests.py
Validates economic guard boundaries and infrastructure limits.

**Purpose:** Test system behavior at economic and infrastructural limits.

**Execution:**
```bash
cd /path/to/qfs-v13
python -m tests.v13_6.BoundaryConditionTests
```

**Evidence Artifact:** `evidence/v13_6/boundary_condition_verification.json`

### 3. FailureModeTests.py
Validates constitutional guard failure modes as "real Open-AGI tests".

**Purpose:** Verify guard behavior under failure conditions with structured error codes.

**Execution:**
```bash
cd /path/to/qfs-v13
python -m tests.v13_6.FailureModeTests
```

**Evidence Artifact:** `evidence/v13_6/failure_mode_verification.json`

### 4. PerformanceBenchmark.py
Validates performance with full guard stack enabled.

**Purpose:** Measure TPS and latency with all constitutional guards active.

**Execution:**
```bash
cd /path/to/qfs-v13
python -m tests.v13_6.PerformanceBenchmark
```

**Evidence Artifact:** `evidence/v13_6/performance_benchmark.json`

## PQC Standardization Tests

### TestPQCStandardization.py
Comprehensive test suite for PQC backend standardization.

**Purpose:** Verify deterministic keygen/sign/verify operations with PQCInterface protocol.

**PQC Backend Selection:**
- **Production:** dilithium-py (when available)
- **Fallback:** MockPQC (SHA-256 simulation for integration testing)

**Execution:**
```bash
cd /path/to/qfs-v13
python -m tests.pqc.TestPQCStandardization
```

**Evidence Artifacts:**
- `evidence/v13_6/pqc_standardization_verification.json`
- `evidence/v13_6/open_agi_reference_scenario.json`

## PQC Backend Information

The PQC implementation follows a standardized approach:

1. **PQCInterface Protocol** - Standardized interface for swappable implementations
2. **Dilithium5Adapter** - Production adapter using dilithium-py
3. **MockPQCAdapter** - Testing adapter using SHA-256 simulation
4. **PQCAdapterFactory** - Backend selection mechanism ("real if available, otherwise deterministic mock")

## Evidence Artifact Interpretation

All evidence artifacts are JSON files containing:

- Test results with pass/fail status
- Structured error codes for failures
- Performance metrics where applicable
- Backend information (especially for PQC tests)
- Timestamps for audit trail purposes

## Running the Full V13.6 Test Suite

To execute all V13.6 test suites with deterministic environment:

```bash
cd /path/to/qfs-v13
export PYTHONHASHSEED=0
export TZ=UTC
python -m tests.v13_6.DeterministicReplayTest
python -m tests.v13_6.BoundaryConditionTests
python -m tests.v13_6.FailureModeTests
python -m tests.v13_6.PerformanceBenchmark
python -m tests.pqc.TestPQCStandardization
```

All tests should pass with 100% success rate. Evidence artifacts are automatically generated in the `evidence/v13_6/` directory.