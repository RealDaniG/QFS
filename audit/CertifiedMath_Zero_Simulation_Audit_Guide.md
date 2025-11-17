# CertifiedMath.py QFS V13 Phase 2/3 Zero-Simulation Audit Guide

## 1. Audit Scope

This guide covers the CertifiedMath.py module for QFS V13 Phase 2/3 Zero-Simulation compliance verification.

### Module Scope
- **CertifiedMath.py**: Deterministic arithmetic (_safe_*), transcendental series, log hashing, Zero-Simulation compliance

### Objective
- Verify deterministic behavior across all inputs and operations
- Confirm audit log integrity and sequencing
- Validate mathematical correctness and series convergence
- Ensure Zero-Simulation compliance (no rounding errors, no nondeterminism, no native floats impacting outputs)

## 2. Preparation

### Environment
- Python ≥ 3.11
- Required packages: pytest
- Secure environment for testing (no external randomness)

### Test Data
Standardized set of deterministic inputs for math functions:

#### BigNum128 Limits
- 0, MAX_VALUE (2^127-1), MIN_VALUE (-2^127), near-boundary fractions
- Negative numbers, zero, small fractions

#### Function-Specific Edge Cases
- φ-Series: ±1.0, ±0.9999 (convergence boundary)
- exp: ±EXP_LIMIT (15.0)
- ln: 0.5, 1, 2, >2, <0.5, negative
- sqrt: 0, very small positive numbers, MAX_VALUE
- two_to_the_power: ±threshold values

### Reference Hashes
For every operation, define a reference SHA256 hash (from a trusted run of Phase 2/3 implementation).
These hashes serve as the Certified V13 Determinism Standard.

## 3. Audit Steps

### Step 1: BigNum128.from_string Verification

#### Truncate-only Behavior
- Test with 18+ decimal digits (should truncate)
- Test with fewer than 18 decimal digits (should pad with zeros)
- Verify: `BigNum128.from_string("123.456789012345678901").to_decimal_string()` = "123.456789012345678900"

#### Integer, Negative, and Zero Input
- Test integer input: `BigNum128.from_string("123").to_decimal_string()` = "123.000000000000000000"
- Test negative input: `BigNum128.from_string("-123.456").to_decimal_string()` = "-123.456000000000000000"
- Test zero input: `BigNum128.from_string("0").to_decimal_string()` = "0.000000000000000000"

#### Deterministic Output Verification
- Confirm output matches reference deterministic value
- Verify identical inputs always produce identical internal representations

### Step 2: Safe Math Functions Verification

#### Basic Arithmetic Operations
Test `_safe_add`, `_safe_sub`, `_safe_mul`, `_safe_div` with:
- MAX_VALUE, MIN_VALUE, 0, 1, -1
- Overflow/underflow detection and exception raising
- Verify deterministic outputs

#### Transcendental Functions

##### φ-Series (_safe_phi_series)
- Test with ±1.0, ±0.9999
- Verify max phi clamp applied (PHI_INTENSITY_B = 0.1)
- Test convergence boundary |x| ≤ 1.0
- Verify series terms count is configurable and deterministic

##### Exponential (_safe_exp)
- Test with ±EXP_LIMIT (15.0), 0
- Verify series truncation at configurable term limit
- Confirm zero-term logging (exp(0) = 1)
- Test convergence within domain limits

##### Natural Logarithm (_safe_ln)
- Test with 0.5, 1, 2, >2, <0.5, negative
- Verify range normalization for inputs outside [0.5, 2.0]
- Confirm deterministic scaling and LN2_CONSTANT usage
- Test domain validation (negative/zero inputs)

##### Square Root (_safe_fast_sqrt)
- Test with 0, very small positive numbers, MAX_VALUE
- Verify deterministic iteration limit enforcement
- Confirm Newton's method convergence behavior
- Test domain validation (negative inputs)

##### Power (_safe_pow)
- Test with positive base values
- Verify implementation as exp(exponent * ln(base))
- Confirm all internal operations are logged and sequenced

##### Two to the Power (_safe_two_to_the_power)
- Test with ±threshold values
- Verify implementation as exp(x * LN2_CONSTANT)
- Confirm threshold check logs violations
- Test domain validation

### Step 3: Log Sequencing Verification

#### Operation Logging
Every operation must log:
- Input parameters
- Output result
- Operation name
- PQC CID
- Quantum metadata
- Sequential log_index

#### Deterministic Sorting
- Verify logs are sorted by log_index before hashing
- Confirm identical operations produce identical log sequences

#### Hash Verification
- Compute `get_log_hash()` after test transactions
- Confirm output matches reference SHA256 hash
- Verify hash consistency across identical operation sequences

#### Deterministic JSON & Serialization
- Verify `json.dumps(..., sort_keys=True)` used in `get_log_hash()` (note: separators parameter not used in current implementation)
- Confirm that all logs are serialized identically across runs, Python versions, and SDK ports
- Validate deterministic serialization with cross-platform consistency checks

### Step 4: Error Handling Verification

#### Overflow/Underflow Detection
- Test addition/subtraction with values that exceed BigNum128 limits
- Verify `MathOverflowError` is raised with appropriate message
- Confirm all arithmetic operations check bounds

#### Domain Validation
- Test invalid inputs for each function:
  - sqrt(negative) → `MathValidationError`
  - ln(negative/zero) → `MathValidationError`
  - exp(|x| > EXP_LIMIT) → `MathValidationError`
  - phi_series(|x| > 1.0) → `MathValidationError`
  - two_to_the_power(|x| > threshold) → `MathValidationError`

#### Exception Consistency
- Ensure all exceptions are deterministic
- Verify exception messages are consistent across runs
- Confirm custom exceptions are used appropriately

#### Overflow/Underflow Across Combined Operations
- Test sequences of operations, not just single calls, for overflow propagation:
  - e.g., `_safe_add(_safe_mul(a, b), c)` with boundary values
  - Ensures the CIR-302 deterministic halt mechanism would trigger correctly
  - Verify exception propagation through nested operations

### Step 5: Cross-Module Integration Checks

#### CertifiedMath ↔ DRV_Packet Integration
- Confirm that CertifiedMath.py interacts correctly with DRV_Packet.py
- Validate that PQC CID and quantum metadata are passed, recorded, and deterministically logged in every wrapper function
- Verify chain linking integrity between math operations and packet creation
- Test deterministic hash propagation from math operations to packet validation

#### SDK Log Context Integration
- Validate LogContext thread-safe handling across modules
- Confirm audit trail consistency between CertifiedMath and other QFS components
- Verify PQC CID correlation across the entire operation chain

### Step 6: Audit Trail Completeness

#### Log Entry Requirements
Each log entry must include:
- `log_index`/sequence number
- `pqc_cid`
- `quantum_metadata`
- Operation inputs and outputs
- Exception events (overflow, invalid domain)
- Timestamps (deterministic source)

#### Audit Trail Integrity
- Check that no log entries are missing or out of order
- Verify complete operation history for complex transaction sequences
- Confirm deterministic log reconstruction from serialized data
- Validate audit trail immutability and tamper evidence

### Step 7: Reference Hash Verification Automation

#### Automated Hash Comparison
Include automated comparison to stored SHA256 reference logs for:
- Single function calls
- Sequential operations
- Edge-case exception flows
- Configuration change scenarios

#### Hash Validation Framework
- Make sure hash mismatch triggers a test failure
- Implement reference hash database for regression testing
- Validate cross-platform hash consistency
- Ensure version-specific hash validation

### Step 8: Stress / Performance Checks

#### High-Volume Determinism
- Run bulk deterministic operations to detect potential bottlenecks or non-determinism under load
- Ensure `_log_operation` remains deterministic under high-volume scenarios
- Verify memory usage consistency under stress conditions

#### Multi-threaded Scenarios
- Execute concurrent math operations with shared log contexts
- Verify deterministic behavior under multi-threaded conditions
- Confirm thread-safe log list handling with LogContext
- Validate performance scaling without compromising determinism

### Step 9: Configuration Consistency Verification

#### Runtime Configuration Testing
Verify that runtime changes to constants do not break:
- Determinism across all math functions
- Reference hash matching for standard operations
- Series convergence for transcendental functions
- Domain validation boundaries

#### Configuration Change Validation
- Test SERIES_TERMS adjustment impact on series functions
- Validate PHI_INTENSITY_B changes affect phi series output
- Confirm EXP_LIMIT modifications update domain boundaries
- Verify configuration persistence and reset behavior

## 4. Integration Verification

### Full Flow Test
Simulate real transaction:
1. Initialize CertifiedMath with audit log
2. Perform sequence of mathematical operations
3. Update logs and compute final system hash
4. Compare against reference SHA256 hash

### Replay Test
1. Re-run same operations multiple times
2. Confirm identical system hash each run
3. Verify deterministic behavior across executions

### Tamper Test
1. Modify input parameters between runs
2. System must produce different hashes
3. Confirm tamper detection through hash mismatch

## 5. Reporting

For the CertifiedMath module, the audit report should include:

| Field | Description |
|-------|-------------|
| Module | CertifiedMath |
| Test Type | Unit, Integration, Edge Case, Tamper |
| Input | Deterministic values used |
| Expected Output | Reference SHA256 or deterministic value |
| Observed Output | Actual value/hash |
| Status | Pass/Fail |
| Notes | Any anomalies, deviations, or confirmations |

## 6. Optional Advanced Audits

### Multi-thread Testing
- Execute concurrent math operations
- Verify `_log_operation` remains deterministic
- Confirm thread-safe log list handling with LogContext

### Quantum Metadata Validation
- Confirm timestamps and entropy metadata matches expectations
- Ensure no drift or non-deterministic randomness in logs

### Configurable Parameters Testing
- Test runtime configuration of:
  - Series terms count
  - Phi intensity damping factor
  - Exponential limit
- Verify all configurations maintain determinism

### Cross-Platform Determinism
- Test Golang/C++ SDK ports against Python reference hashes
- Confirm full parity across implementations
- Validate deterministic serialization across platforms

## 7. Audit Completion Criteria

CertifiedMath.py is considered audit-compliant when:

- [ ] All unit and integration tests pass
- [ ] Reference deterministic hashes match for all flows
- [ ] Truncate-only precision is maintained
- [ ] Deterministic JSON serialization is used with `sort_keys=True`
- [ ] All mathematical operations produce bit-identical results
- [ ] Audit logs are complete, sequenced correctly, and include all required fields
- [ ] No unhandled exceptions in normal or edge-case scenarios
- [ ] Cross-module integration with DRV_Packet and SDK context verified
- [ ] Combined operation overflow/underflow detection works correctly
- [ ] Reference hash verification automation is implemented and functional
- [ ] Performance/stress testing confirms deterministic behavior under load
- [ ] Configuration changes maintain determinism and reference hash consistency
- [ ] Documentation is updated with constants, limits, and procedure

## Constants and Limits Reference

### BigNum128 Specifications
- **Range**: ±2^127
- **Precision**: 18 decimal places
- **Scale Factor**: 10^18

### Function Limits
| Function | Limit | Notes |
|----------|-------|-------|
| `_safe_ln` | Convergence range [0.5, 2.0] | Values outside normalized using ln(2) |
| `_safe_exp` | |x| ≤ 15.0 | Series truncation enforced |
| `_safe_phi_series` | |x| ≤ 1.0 | Max phi clamp applied |
| `_safe_two_to_the_power` | |x| ≤ EXP_LIMIT / LN2_CONSTANT | Threshold check |

### Configuration Constants
- `PHI_INTENSITY_B` = 0.1 (phi series intensity damping)
- `LN2_CONSTANT` = 0.693147180559945309 (natural log of 2)
- `EXP_LIMIT` = 15.0 (exponential function limit)
- `SERIES_TERMS` = 31 (default series convergence terms)

✅ **Result**: This process ensures 100% Zero-Simulation compliance, traceability, and mathematical integrity for QFS V13 Phase 2/3.