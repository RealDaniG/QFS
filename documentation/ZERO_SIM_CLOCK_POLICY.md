# Zero-Simulation Global Clock Policy

> [!IMPORTANT]
> **Strict Enforcement Required**
> This document defines the **single source of truth** for time in the Quantum Financial System (QFS) V13.
> Any deviation from this policy constitutes a **critical security violation** (CIR-302).

## 1. Canonical Time Definition

All modules must use the **Canonical Deterministic Timestamp** defined below.

| Property | Specification | Rationale |
| :--- | :--- | :--- |
| **Unit** | **Nanoseconds** (integer) | Sufficient precision for HFT without floating-point errors. |
| **Origin** | **Genesis Block Timestamp** (0) | Absolute reference point, independent of wall-clock time. |
| **Encoding** | **BigNum128** (or pure Python `int`) | Prevents overflow/underflow and floating-point non-determinism. |
| **Rounding** | **Floor** (Truncation) | Deterministic rounding rule for any conversions. |
| **Source** | `DRV_Packet.ttsTimestamp` | The ONLY valid source of time. |

### 1.1 Forbidden Time Sources

The following are **STRICTLY PROHIBITED**:

- `time.time()`
- `datetime.now()`
- `os.times()`
- `perf_counter()`
- Any system clock or hardware timer.

## 2. DeterministicTime Module Contract

The `src.libs.DeterministicTime` module is the **sole provider** of time logic.

### 2.1 Core API

```python
def canonical_time_from_packet(packet: DRV_Packet) -> int:
    """
    Extracts and validates the canonical timestamp from a DRV Packet.
    
    Must verify:
    1. Packet PQC signature is valid.
    2. Packet sequence is monotonic (greater than previous).
    3. Timestamp is non-negative.
    """
    pass
```

### 2.2 Side-Effect Free Guarantee

All functions in `DeterministicTime` must be **pure functions**:

- No I/O operations.
- No global state mutation.
- No random number generation.
- No system calls.

## 3. Strict Evidence Format

All economics modules must log evidence in the following strict JSON format:

```json
{
  "event": "<EventName>",
  "canonical_timestamp": 1234567890000000000,
  "timestamp_source": "drv_packet:<SequenceNumber>",
  "packet_hash": "<SHA256_Hash_of_Packet>",
  "pqc_level": "<PQC_Algorithm_Name>",
  "deterministic_inputs": {
    "param_1": "value_1",
    "param_2": "value_2"
  },
  "state_changes": {
    "balance_before": "100.000000000000000000",
    "balance_after": "105.000000000000000000"
  }
}
```

### 3.1 Required Fields

- `canonical_timestamp`: The integer nanosecond timestamp.
- `timestamp_source`: Must be `drv_packet:<seq>`.
- `packet_hash`: Cryptographic link to the source packet.
- `pqc_level`: The PQC algorithm used to sign the packet (e.g., "Dilithium5").

## 4. Error Handling Policy

Violations of time policy must trigger immediate failure.

| Scenario | Action | Error Type |
| :--- | :--- | :--- |
| Invalid PQC Signature | **Reject Transaction** | `SecurityViolation` |
| Non-Monotonic Time | **Reject Transaction** | `TimeRegressionError` |
| Negative Timestamp | **Reject Transaction** | `InvalidTimestampError` |
| Timestamp Overflow | **Reject Transaction** | `TimestampOverflowError` |
| Floating-Point Time | **Crash / CIR-302** | `ZeroSimViolation` |

## 5. Verification & Enforcement

### 5.1 CI/CD Pipeline

The `zero_sim_verify.sh` script runs on every commit to enforce:

1. **AST Scan**: No forbidden functions.
2. **Import Scan**: No forbidden modules.
3. **Replay Test**: Deterministic output verification.

### 5.2 Runtime Enforcement

- `AST_ZeroSimChecker` runs at startup.
- `DeterministicTime` validates every timestamp access.
