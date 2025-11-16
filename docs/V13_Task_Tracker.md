# QFS V12 → V13 Autonomous Audit & Migration Plan

## Objective
Enforce Zero-Simulation Compliance, Deterministic Operations, CertifiedMath Governance, and Atomic Multi-Token Coherence during migration. Each file and service must be audited, remediated, and verified before moving to the next. No shortcuts.

---

## Phase 0: Preparation

### Environment Lockdown
- [ ] Install Node.js 18+ and Python 3.10+
- [ ] Lock all dependencies (package-lock.json / requirements.txt)
- [ ] Verify deterministic compiler versions (Solidity, TS/JS, Python)
- [ ] Confirm PostgreSQL 14+ setup and migrations
- [ ] Create empty audit log folder: /audit_logs

### Baseline Repository Snapshot
- [ ] Record current git commit hash
- [ ] Create V12 full backup
- [ ] Document current folder/file structure in docs/V12_FileMap.md

### Audit & Enforcement Tooling
- [ ] Install/verify AST-based Zero-Simulation Checker (scripts/zero-sim-ast.js)
- [ ] Prepare CertifiedMath test harness (tests/certifiedmath/)
- [ ] Initialize PQC test environment (Dilithium/Kyber precompiled)

---

## Phase 1: File-by-File Core Audit (Mandatory Step-By-Step)

### Rules
- Each file must pass AST zero-sim check
- Each arithmetic must use CertifiedMath only
- PQC must be integrated if signatures are used
- Only when one file passes the audit and tests, move to the next

### Step 1. Core Math

#### File: CertifiedMath_fixed.py
- [ ] Run full AST check
- [ ] Replace native floats/BigNumber with _safe_* fixed-point functions
- [ ] Add full test coverage (unit + edge cases)
- [ ] Log audit results: /audit_logs/CertifiedMath_fixed.log

#### File: CertifiedMath_final.py
- [ ] Verify consistency with fixed version
- [ ] Remove redundant/unverified math functions
- [ ] Confirm audit log integration

### Step 2. Core Engines

#### File: ActionCostEngine.py
- [ ] Enforce CertifiedMath in all calculations
- [ ] Integrate PQC validation for any external input
- [ ] Add deterministic test vectors
- [ ] Record audit log

#### File: AtomicCommit.py
- [ ] Ensure all commits go through AtomicTxCoordinator
- [ ] Add CIR-302 deterministic halt for failed commits
- [ ] Unit test failure injection
- [ ] Log audit results

#### File: CoherenceLedger.py
- [ ] Integrate PQC-signed ledger entries
- [ ] Validate deterministic serialization
- [ ] Ensure single canonical stateRootCID per commit
- [ ] Document audit results

### Step 3. Tokens (Core PQC + CertifiedMath)

Order is critical: audit FLX → ATR → PSY → RES

#### File: FLX.sol
- [ ] Replace BigNumber math with deterministic fixed-point math
- [ ] Verify PQC signature verification (Dilithium)
- [ ] Add event emission for mint/burn
- [ ] Add access control modifiers
- [ ] Audit log pass

#### File: ATR.sol
- [ ] Enforce CertifiedMath for alpha-field calculations
- [ ] PQC verification for all input updates
- [ ] Validate HSMF coherence metric integration
- [ ] Log audit completion

#### File: PSY.sol
- [ ] Phi-based resonance calculations use CertifiedMath
- [ ] PQC verification for all timestamps
- [ ] Add audit trail for reward calculation
- [ ] Confirm deterministic output across multiple runs

#### File: RES.sol
- [ ] Implement AtomicTxCoordinator interface
- [ ] PQC verification for consensus updates
- [ ] Ensure multi-token back-commit is atomic
- [ ] Log audit results

---

## Phase 2: Utility Contracts Audit

### Step 4. Penalty Contract
- [ ] Verify PQC signature verification
- [ ] Add appeal mechanism & audit logging
- [ ] Replace any floating-point calculations

### Step 5. Staking Contract
- [ ] CertifiedMath for reward calculation
- [ ] Add emergency withdrawal mechanism
- [ ] Add deterministic test vectors

---

## Phase 3: Security Hardening

### PQC Key Governance
- [ ] Key generation & deterministic rotation
- [ ] Revocation list checks
- [ ] CIR-302 halt triggers for invalid PQC operations

### Access Control & Reentrancy
- [ ] Add role-based access modifiers
- [ ] Ensure Checks-Effects-Interactions pattern
- [ ] Commit-reveal schemes where needed

### Audit Logging
- [ ] CertifiedMath operations logged
- [ ] PQC key events logged
- [ ] CIR-302 events logged
- [ ] All logs PQC-hashed and stored /audit_logs/

---

## Phase 4: Testing & Verification

### Unit Tests
- [ ] 100% coverage for each audited file
- [ ] Deterministic test vectors only (no mocks)
- [ ] Cross-runtime consistency (Python, JS, Solidity)

### Integration Tests
- [ ] Multi-token transactions verified end-to-end
- [ ] Failure injection for AtomicTxCoordinator
- [ ] CIR-302 deterministic halts tested

### Performance Checks
- [ ] Gas optimization and transaction cost benchmarking
- [ ] Deterministic execution timing

---

## Phase 5: Reporting & Sign-Off

### Audit Logs
- [ ] Compile /audit_logs/*.log into V13_Audit_Report.md
- [ ] Include PQC verification, deterministic math, and AST checker results

### Migration Readiness
- [ ] Confirm all files passed step-by-step audit
- [ ] No floating-point math, no native randomness
- [ ] PQC integration verified

---

## Enforcement Rules

### Cannot proceed to next file until the current file passes:
- [ ] AST zero-sim check ✅
- [ ] CertifiedMath deterministic validation ✅
- [ ] PQC signature verification ✅ (if applicable)
- [ ] Audit log generated ✅

### No mock data allowed:
- [ ] Every test must use real deterministic vectors
- [ ] Any deviation triggers CIR-302 audit flag