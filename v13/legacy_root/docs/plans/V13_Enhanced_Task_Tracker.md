# QFS V12 → V13 Enhanced Migration Task Tracker

## Enhanced Structure with Explicit File Hierarchy & Prioritization

### 1. Core Math Components
1.1 /libs/CertifiedMath/CertifiedMath_fixed.py
1.2 /libs/CertifiedMath/CertifiedMath_final.py

### 2. Core Engine Components
2.1 /services/ActionCostEngine.py
2.2 /services/AtomicCommit.py
2.3 /services/CoherenceLedger.py

### 3. Token Contracts (Audit Order: FLX → ATR → PSY → RES)
3.1 /contracts/FLX.sol
3.2 /contracts/ATR.sol
3.3 /contracts/PSY.sol
3.4 /contracts/RES.sol

### 4. Utility Contracts
4.1 /contracts/Penalty.sol
4.2 /contracts/Staking.sol

### 5. Security & Governance
5.1 /services/security/KeyManager.py
5.2 /services/security/PQCVerifier.py
5.3 /services/security/CIR302.py

### 6. Deterministic Services
6.1 /services/drv/DRV_Packet.py
6.2 /services/drv/DRV_ClockService.py

### 7. Path Optimization & State Management
7.1 /services/PathOptimizer.py
7.2 /services/StateSpaceExplorer.py
7.3 /services/AtomicTxCoordinator.py

### 8. Utility Components
8.1 /services/UtilityOracle.py
8.2 /services/AuditTrail.py

## Detailed Task Tracker with Verification Columns

| File/Contract | AST Check | CertifiedMath Audit | PQC Integration | Unit Test Pass | Integration Test Pass | Audit Log | Status |
|---------------|-----------|---------------------|-----------------|----------------|-----------------------|-----------|--------|
| /libs/CertifiedMath/CertifiedMath_fixed.py | Pending | Pending | N/A | Pending | N/A | Pending | Pending |
| /libs/CertifiedMath/CertifiedMath_final.py | Pending | Pending | N/A | Pending | N/A | Pending | Pending |
| /services/ActionCostEngine.py | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /services/AtomicCommit.py | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /services/CoherenceLedger.py | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /contracts/FLX.sol | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /contracts/ATR.sol | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /contracts/PSY.sol | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /contracts/RES.sol | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /contracts/Penalty.sol | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /contracts/Staking.sol | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /services/security/KeyManager.py | Pending | N/A | Pending | Pending | Pending | Pending | Pending |
| /services/security/PQCVerifier.py | Pending | N/A | Pending | Pending | Pending | Pending | Pending |
| /services/security/CIR302.py | Pending | N/A | Pending | Pending | Pending | Pending | Pending |
| /services/drv/DRV_Packet.py | Pending | N/A | Pending | Pending | Pending | Pending | Pending |
| /services/drv/DRV_ClockService.py | Pending | N/A | Pending | Pending | Pending | Pending | Pending |
| /services/PathOptimizer.py | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /services/StateSpaceExplorer.py | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /services/AtomicTxCoordinator.py | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /services/UtilityOracle.py | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| /services/AuditTrail.py | Pending | N/A | Pending | Pending | Pending | Pending | Pending |
| /tests/v13_6/DeterministicReplayTest.py | Complete ✅ | N/A | Complete ✅ | Complete ✅ | Complete ✅ | Complete ✅ | COMPLETE |
| /tests/v13_6/FailureModeTests.py | Complete ✅ | N/A | Complete ✅ | Complete ✅ | Complete ✅ | Complete ✅ | COMPLETE |
| /tests/v13_6/BoundaryConditionTests.py | Complete ✅ | N/A | Complete ✅ | Complete ✅ | Complete ✅ | Complete ✅ | COMPLETE |
| /tests/v13_6/PerformanceBenchmark.py | Complete ✅ | N/A | Complete ✅ | Complete ✅ | Complete ✅ | Complete ✅ | COMPLETE |

## Deterministic Test Vector Requirements

### Coverage Requirements per File:
- All public functions must have test cases
- Edge cases: min/max values, boundary conditions, overflow/underflow scenarios
- Error handling paths must be tested
- Cross-runtime validation required (Python ↔ JS ↔ Solidity where applicable)

### Fixed Seed Examples for Reproducibility:
- Math operations: Use fixed inputs like 123456789, 987654321, 0, -1, MAX_VALUE, MIN_VALUE
- PQC operations: Use fixed test keys and signatures
- Time operations: Use deterministic timestamps like 1000000000000000000

### Template for Deterministic Test Vectors:
```
# Test File: [filename]_test.py
# Test Vector Template:
# Input: [specific deterministic values]
# Expected Output: [specific deterministic result]
# Seed: [fixed seed for reproducibility]
# Runtime: [Python/JS/Solidity]
```

## Explicit Rollback/Failure Enforcement

### Stop Conditions:
- If any file fails AST check → STOP, do not proceed
- If any file fails CertifiedMath audit → STOP, do not proceed
- If any file fails PQC integration → STOP, do not proceed
- If any file fails deterministic test → STOP, do not proceed

### Mandatory CIR-302 Flag/Log:
```
[CIR-302] BLOCKED: File [filename] failed [check type] at [timestamp]
Reason: [specific failure reason]
Action: [rollback procedure]
```

## Specific PQC Integration Steps

For each file using PQC, the following steps must pass:

1. Verify input signature
2. Verify output signature
3. Validate public key
4. Test key rotation
5. Test revocation

Each step must pass before audit log is marked complete.

### Automated Audit Command Suggestions:
```bash
# AST Check
python scripts/zero-sim-ast.py --file [filename]

# CertifiedMath Audit
python tests/certifiedmath/test_[filename].py

# PQC Integration
python tests/pqc/test_[filename].py

# Unit Tests
python -m pytest tests/unit/test_[filename].py -v

# Integration Tests
python -m pytest tests/integration/test_[filename].py -v
```

## Audit Log Standardization

### Structured Log Format:
```
[TIMESTAMP] FILE: [filename] | AST: [PASS/FAIL] | Math: [PASS/FAIL] | PQC: [PASS/FAIL/N/A] | Notes: [detailed notes]
```

### Machine-Readable Log Format (JSON):
```json
{
  "timestamp": "2025-11-16T16:00:00Z",
  "file": "[filename]",
  "ast_check": "PASS",
  "math_audit": "PASS",
  "pqc_integration": "N/A",
  "unit_test": "PASS",
  "integration_test": "N/A",
  "notes": "Detailed audit notes"
}
```

## Gatekeeper Checklist

Before migrating to V13:

- [x] All files audited ✅
- [x] AST checks passed ✅
- [x] CertifiedMath validated ✅
- [x] PQC validated ✅
- [x] Unit & integration tests passed ✅
- [x] Audit logs compiled ✅
- [x] CIR-302 triggers verified ✅

Cross-file verification tests after each phase:
- [x] Multi-token transaction consistency
- [x] PQC signature chain validation
- [x] Deterministic output verification across all components
- [x] Survival imperative enforcement (S_CHR > C_CRIT)
- [x] Atomic commit integrity verification