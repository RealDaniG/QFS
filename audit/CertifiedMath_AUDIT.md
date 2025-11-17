# CertifiedMath Audit Documentation

This document provides comprehensive information about the CertifiedMath library for auditors, including constants, limits, integration instructions, and compliance features.

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `PHI_INTENSITY_B` | 0.1 | Phi series intensity damping factor |
| `LN2_CONSTANT` | 0.693147180559945309 | Natural logarithm of 2, used for range normalization |
| `EXP_LIMIT` | 15.0 | Maximum absolute value for exponential function input |
| `SERIES_TERMS` | 31 | Default number of terms for series convergence |

## Limits

### BigNum128
- **Range**: ±2^127
- **Precision**: 18 decimal places
- **Scale Factor**: 10^18

### Function-Specific Limits

| Function | Limit | Notes |
|----------|-------|-------|
| `_safe_ln` | Convergence range [0.5, 2.0] | Values outside this range are normalized using ln(2) |
| `_safe_exp` | |x| ≤ 15.0 | Series truncation enforced at this limit |
| `_safe_two_to_the_power` | |x| ≤ EXP_LIMIT / LN2_CONSTANT | Threshold check logs violations |

## Integration Instructions

### 1. DRV_Packet Integration (Required for All Audited Calls)

All math operations must be associated with a Deterministic Replayable Validation Packet (DRV_Packet) for full traceability:

```python
# Create a log list for deterministic operations
audit_log_store = []

# Wrap operations in LogContext for thread safety
with LogContext(audit_log_store) as ctx_log:
    cm = CertifiedMath(ctx_log)
    
    # All operations must include PQC CID and quantum metadata
    result = cm.add(a, b, pqc_cid="YOUR_PQC_CID", quantum_metadata={"source": "your_module"})
```

### 2. LogContext Usage

The LogContext ensures thread-safe handling of the log list:

```python
from CertifiedMath import LogContext

audit_log_store = []
with LogContext(audit_log_store) as ctx_log:
    cm = CertifiedMath(ctx_log)
    # Perform operations...
```

### 3. PQC CID and Quantum Metadata

Every top-level call must include a PQC correlation ID and quantum metadata:

```python
result = cm.exp(value, 
                pqc_cid="QFSV13-PQC-BUNDLE-001", 
                quantum_metadata={"phase": "V13 Phase 3", "entropy_level": "QRNG-VDF"})
```

## Auditor Notes

### Deterministic Hash Verification

The deterministic hash (`get_log_hash()`) confirms sequence integrity:

```python
# After operations, verify the deterministic hash
bundle_hash = cm.get_log_hash()
# Identical operations will always produce identical hashes
```

### Thread Safety

The `LogContext` wrapper ensures multi-threaded reproducibility:

- Each thread should use its own log list
- Operations within a LogContext are sequentially indexed
- Thread-safe append ensures deterministic ordering

### Exception Handling

All exceptions trigger CIR-302 or higher-level fail-safes:

| Exception | Trigger Condition | CIR Level |
|-----------|-------------------|-----------|
| `MathOverflowError` | Arithmetic overflow/underflow | CIR-302 |
| `MathValidationError` | Invalid inputs or domain errors | CIR-302 |
| `MathSerializationError` | Serialization/deserialization failures | CIR-302 |

## Performance Optimizations

### Precomputed Constants
- Factorials for `_safe_exp` series are computed deterministically
- LN2_CONSTANT is precomputed for range normalization

### Bit-Shift Operations
- Powers of two use bit-shift optimization in `_safe_two_to_the_power`

### Memoization/Caching
- Transcendental functions do not currently implement caching to maintain deterministic behavior
- All operations are recomputed each time for audit trail integrity

### Vectorized Batch Operations
- Not currently implemented to maintain operation-by-operation auditability
- Future implementations would process arrays deterministically with individual operation logging

## Compliance Features

### Zero-Simulation Compliance
- All operations are deterministic and bit-identical across platforms
- Integer-only arithmetic ensures no floating-point variance
- Fixed iteration counts for all series computations

### Per-Operation Auditing
- Every arithmetic step is logged with sequential indexing
- All inputs, outputs, and intermediate results are recorded
- PQC CID correlation ensures bundle traceability

### Configurable Precision
- Series terms can be adjusted at runtime while maintaining determinism
- Phi intensity damping is configurable
- Exponential limits are configurable

This documentation ensures auditors can verify that CertifiedMath meets all QFS V13 Phase 2/3 Zero-Simulation compliance requirements.