# Zero-Sim Auth Compliance

**Objective:** Ensure all authentication flows respect the Zero-Simulation principle: Determinism, Replayability, auditable Causality.

## 1. Deterministic Session IDs

- **Requirement:** `session_id` must be derived from `hash(counter + node_seed + wallet_address)`.
- **Allowed:** Monotonic counters, stable seeds.
- **Forbidden:** `uuid.v4()`, timestamp-based entropy.

## 2. EvidenceBus Replay

- **Requirement:** Session state (Validity, Scopes, Device Binding) must be reproducible *bit-for-bit* by replaying `SESSION_*` events.
- **Verification:** `tests/replay/auth_golden_trace.py` asserts `Replay(Log) == LiveState`.

## 3. Device Hash Determinism

- **Requirement:** `computeDeviceHash()` must yield stable output for the same environment.
- **Inputs:** OS Family, CPU Arch, Install UUID (Static).
- **Forbidden:** Volatile telemetry, clock drift.

## 4. MOCKPQC Signatures

- **Requirement:** Signatures must be deterministic hashes of `(message + key_stub)`.
- **Forbidden:** Randomized nonces in MOCKPQC mode.
