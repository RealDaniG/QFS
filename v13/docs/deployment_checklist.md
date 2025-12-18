# Phase IV Entry: Deployment Readiness Checklist

**Goal:** Ensure the system is ready for real-world integration (Stage/Prod).
**Gatekeeper:** CI/CD Pipeline (`phase3-integration-gate`)

## 1. System Invariants

- [ ] **Canonical Schema Adherence**: All external calls verified against `v13.libs.canonical` Pydantic models.
- [ ] **BigNum128 Integrity**: Rewards and balances must remain string-typed `BigNum128` (18 decimals) end-to-end.
- [ ] **PQC Signatures**: `AdvisorySignal` payloads must be verified using `v13.libs.pqc` (real signatures, not mocks).

## 2. Gatekeeper Tests

Ensure these pass on every PR:

- [ ] `tests/unit/test_certified_math_import.py` (Smoke Test)
- [ ] `tests/contract/test_api_contracts.py` (Schema Golden Paths)
- [ ] `tests/integration/test_lifecycle.py` (E2E Scenario)

## 3. Exit Conditions for Phase III

- [ ] **CertifiedMath Ubiquity**: All legacy math calls in `economics` module replaced with `CertifiedMath`.
- [ ] **Zero Red Builds**: Contract tests pass for 7 consecutive days.
- [ ] **Float Eradication**: No direct float arithmetic in result paths.

## 4. Operational Readiness

- [ ] **Logging**: Structured logs (JSON) enabled for all `EconomicEvent`.
- [ ] **Monitoring**: Metrics for API schema validation failures.
- [ ] **Secrets**: PQC keys loaded from secure vault (not env vars).
