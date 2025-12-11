# QFS V13 - Comprehensive Verification Plan
## Addressing Missing & Underrepresented Items

This document provides a detailed verification plan that addresses all the missing and underrepresented items from the original checklist, ensuring 100% coverage of QFS V13 Phase 1-3 requirements.

---

## Phase 1 – BigNum128 & CertifiedMath

### BigNum128

#### Explicit Underflow Check in Fractional Parsing
- [x] Verify underflow detection for fractional parts beyond SCALE_DIGITS
- [x] Test case: 0.0000000000000000011 should trigger underflow error
- [x] Confirm BigNum128Error is raised for underflow conditions
- [x] Verify deterministic rounding behavior for edge cases
- [x] Created and ran unit tests for underflow cases

#### Edge-case Arithmetic with MAX_VALUE
- [ ] Test addition: MAX_VALUE + 1 → OverflowError
- [ ] Test multiplication: MAX_VALUE * 2 → OverflowError
- [ ] Test subtraction: 0 - 1 → BigNum128Error (underflow)
- [ ] Test division: MAX_VALUE / very_small_value → Overflow protection

#### Copy Method Deterministic Behavior
- [x] Verify copy() method produces identical value in single-threaded context
- [x] Test copy() behavior in simulated multithreaded scenarios
- [x] Confirm no shared state between original and copied instances
- [x] Validate copy() works correctly with edge values (0, MAX_VALUE, SCALE)
- [x] Created and ran comprehensive copy method tests

#### Unit Test Coverage of Operator Overloads
- [x] __eq__: Test equality with identical values, different instances
- [x] __lt__: Test less-than with various value combinations
- [x] __le__: Test less-than-or-equal edge cases
- [x] __gt__: Test greater-than with boundary values
- [x] __ge__: Test greater-than-or-equal edge cases
- [x] __ne__: Test inequality with identical and different values
- [x] Created and ran comprehensive operator overload tests

### CertifiedMath

#### Self-test Hash Verification
- [x] Verify PROOF_VECTORS produce identical hashes across platforms
- [x] Test hash reproducibility on Linux, Windows, macOS
- [x] Confirm log hash verification for all 13 functions
- [x] Validate cross-platform bit-perfect results

#### Edge-case Inputs for Transcendental Functions
- [x] Test very small fractions (near 1e-18) for all functions
- [x] Test very large integers (near MAX_VALUE) for all functions
- [x] Validate sin(π/2), cos(0), erf(0) produce exact expected values
- [x] Confirm exp(0) = 1, ln(1) = 0 with precise hash verification
- [x] Created and ran comprehensive edge-case tests for transcendental functions

### Zero-Simulation

#### AST Checks for Hidden Float Creation
- [x] Verify no implicit float creation via integer division
- [x] Check // operator does not produce float results
- [x] Confirm all math operations remain in integer domain
- [x] Validate json, hashlib imports are Zero-Sim safe
- [x] Enhanced AST_ZeroSimChecker to detect scientific notation floats
- [x] Enhanced AST_ZeroSimChecker to detect dynamic imports
- [x] Enhanced AST_ZeroSimChecker to detect global attribute mutation
- [x] Enhanced AST_ZeroSimChecker with improved error handling

#### Legacy Module Zero-Sim Compliance
- [x] Audit all imported libraries for Zero-Simulation compliance
- [x] Verify json module usage does not introduce non-determinism
- [x] Confirm hashlib produces consistent results across platforms
- [x] Check for any hidden time, random, or platform-dependent calls
- [x] Created and ran comprehensive tests for forbidden module imports

---

## Phase 2 – Tokens & HSMF

### TokenStateBundle / StateTransitionEngine

#### Token Immutability Verification
- [ ] Confirm CHR, FLX, ATR, RES, ΨSync cannot be mutated after creation
- [ ] Test accidental mutation attempts raise appropriate errors
- [ ] Verify all token access is through immutable properties
- [ ] Validate copy/clone operations preserve immutability

#### Edge-case Stress Tests
- [ ] Test simultaneous minimum values for all 5 tokens
- [ ] Test simultaneous maximum values for all 5 tokens
- [ ] Validate mixed min/max states across token types
- [ ] Confirm atomic rollback on any token overflow/underflow

#### Deterministic Hash for PQC Signing
- [ ] Verify entire token bundle produces deterministic hash
- [ ] Test hash consistency across multiple serialization runs
- [ ] Confirm PQC signing works with bundle hash
- [ ] Validate hash changes when any token value changes

### HSMF

#### Frequency_metric Comparison Edge Cases
- [ ] Test frequency_metric comparison to ONE with exact equality
- [ ] Validate comparisons with values slightly above/below ONE
- [ ] Confirm edge cases near zero and maximum values
- [ ] Verify floating-point-like comparisons use proper BigNum128 methods

#### Reward Allocation Deterministic Sorting
- [ ] Test deterministic sorting with identical metric values
- [ ] Validate tie-breaking mechanism for same addresses
- [ ] Confirm sorted order is consistent across runs
- [ ] Verify sorting works with edge-case address values

#### c_holo Extremes Stress Test
- [ ] Test c_holo = 0 behavior (reward suppression)
- [ ] Test c_holo = 1 behavior (maximum reward)
- [ ] Validate values slightly above/below extremes
- [ ] Confirm boundary conditions trigger expected behaviors

---

## Phase 3 – Time, Coherence & Integration

### DeterministicTime

#### Monotonicity Enforcement Edge Cases
- [ ] Test skipped timestamp packets trigger CIR-302
- [ ] Validate time regression detection and halting
- [ ] Confirm boundary conditions for timestamp values
- [ ] Verify PQC metadata includes timestamp and packet hash

#### PQC Metadata Verification
- [ ] Confirm timestamp included in PQC signing
- [ ] Validate packet hash inclusion in metadata
- [ ] Test metadata consistency across runs
- [ ] Verify PQC signature validation for time metadata

### DRV_Packet / PsiFieldEngine

#### Canonical Serialization Tests
- [ ] Verify repeated serialization produces identical byte strings
- [ ] Test serialization consistency across platforms
- [ ] Confirm all fields included in canonical representation
- [ ] Validate serialization with edge-case values

#### Cycle Hashing Normalization
- [ ] Test rotation normalization for edge-length cycles
- [ ] Verify inversion normalization works correctly
- [ ] Confirm hash consistency for equivalent cycles
- [ ] Validate cycle detection with complex graph structures

### Economic Adversary Suite

#### Evidence Logging for Replay/Audit
- [ ] Verify all adversary actions logged with evidence
- [ ] Test log consistency for replay scenarios
- [ ] Confirm audit trail includes all relevant data
- [ ] Validate evidence format for CIR triggers

#### Edge-case Synthetic Adversaries
- [ ] Test minimal δ token input attacks
- [ ] Validate zero-state attack scenarios
- [ ] Confirm boundary condition adversaries blocked
- [ ] Verify synthetic adversaries produce canonical evidence

### Integration Components

#### PQC Signature Ordering
- [ ] Confirm all orchestrators respect PQC signature ordering
- [ ] Validate signature chain integrity
- [ ] Test signature validation across components
- [ ] Verify ordering consistency in distributed scenarios

#### RewardAllocator Rounding Behavior
- [ ] Test rounding behavior with maximum token states
- [ ] Validate rounding with minimum token states
- [ ] Confirm consistency across all boundary conditions
- [ ] Verify rounding does not introduce bias

---

## Phase 3 – Security, Verification & Compliance

### Security & PQC

#### Cross-platform Signature Verification
- [ ] Test Dilithium signature verification on Linux
- [ ] Test Dilithium signature verification on Windows
- [ ] Test Dilithium signature verification on macOS
- [ ] Confirm signature consistency across Python versions

#### Historical State Transition Hash Linking
- [ ] Verify all historical state transitions are signed
- [ ] Confirm hash linking between consecutive states
- [ ] Validate integrity of entire state history
- [ ] Test tamper detection in historical chain

### Determinism & Replay

#### Serialization Hash Consistency
- [ ] Verify log serialization produces identical SHA256
- [ ] Confirm Dilithium signature consistency across runs
- [ ] Test manifest serialization hash reproducibility
- [ ] Validate all serialized outputs are deterministic

### Testing & Verification

#### Edge-case BigNum128 Multiplication
- [ ] Test MAX_VALUE × MAX_VALUE → deterministic overflow
- [ ] Validate overflow protection mechanisms
- [ ] Confirm error reporting consistency
- [ ] Verify intermediate overflow detection

#### HSMF Fractional Perturbation Stress Test
- [ ] Test perturbations near zero values
- [ ] Validate perturbations near ONE values
- [ ] Confirm edge-case handling consistency
- [ ] Verify no unexpected behavior at boundaries

### Documentation & Style

#### Exception Audit Notes
- [ ] Include audit notes for every exception raised
- [ ] Document exception causes and handling
- [ ] Verify audit notes are implementation-specific
- [ ] Confirm exception documentation completeness

#### Canonical JSON Log Ordering
- [ ] Verify canonical ordering of JSON logs
- [ ] Test key sorting consistency
- [ ] Confirm value serialization determinism
- [ ] Validate log structure across platforms

---

## Phase 3 Evidence Package

### PQC Signatures for Individual Files
- [ ] Verify manifest includes PQC signatures for every file
- [ ] Test individual file signature validation
- [ ] Confirm signature chain integrity
- [ ] Validate signature consistency across runs

### JSONL Log Hash Chain
- [ ] Include hash chain of JSONL logs
- [ ] Test tamper detection in log chain
- [ ] Verify chain integrity validation
- [ ] Confirm prevention of log manipulation

---

## Extra / "Nothing Left Out"

### Explicit Fractional Rounding Tests
- [ ] Test all arithmetic combinations with fractional rounding
- [ ] Validate round-half-up behavior consistently
- [ ] Confirm no bias in rounding operations
- [ ] Verify rounding edge cases handled correctly

### Hidden Global State Check
- [ ] Confirm no accidental hidden global state
- [ ] Test helper functions for state independence
- [ ] Validate internal caches do not persist state
- [ ] Verify clean state between operations

### CI Pipeline Audit Reports
- [ ] Confirm CI pipeline produces PQC hash reports
- [ ] Verify CI pipeline produces SHA256 audit reports
- [ ] Test report consistency across runs
- [ ] Validate report completeness

---

## Summary of Enhanced Coverage

This verification plan addresses all the missing and underrepresented items by adding:

1. **Edge-case arithmetic & fractional underflow/overflow tests** (BigNum128 + CertifiedMath)
2. **Canonical serialization + hash verification** for all components (including orchestrators, PsiField, logs)
3. **Historical state & log PQC hash linking** for full auditability
4. **Edge-case adversary testing** (near-zero, near-max token states)
5. **Explicit documentation of rounding, tie-breaking, and deterministic sorting**

Each item in this plan must be verified and checked off to ensure 100% compliance with QFS V13 requirements.