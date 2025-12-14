# Zero-Sim Compliance Review Queue

> **Generated:** 2025-12-14
> **Status:** PENDING REVIEW

The following violations were detected but **not automatically fixed** due to risk of breaking functionality or requiring architectural decisions.

## Critical Violations (Review Required)

### 1. Random Usage in IDs (Frontend/Hooks)

**Files:**

- `v13/ATLAS/src/hooks/useInteraction.ts`
- `v13/ATLAS/src/hooks/useProfileUpdate.ts`
- `v13/ATLAS/src/lib/content/publisher.ts`
- `v13/ATLAS/src/lib/governance/service.ts`

**Issue:** usage of `crypto.randomUUID()` for `pendingId`.
**Recommendation:** Determine if these IDs are persisted to the authoritative ledger. If they are just for client-side optimistic UI, they might be acceptable. If they become canonical Event IDs, they violate determinism unless the Ledger re-assigns a deterministic ID upon ingestion.
**Action:** Confirm `RealLedger` re-hashes IDs or accepts them as "Client IDs" (non-canonical).

### 2. Random Usage in Audit Scripts

**Files:**

- `v13/docs/audit/phase_a_module_audit.py`
- `v13/docs/audit/qfs_v13_autonomous_audit.py`
- `v13/scripts/zero-sim-ast.js`

**Issue:** Scripts contain the *text* "random.random" which triggers the scanner.
**Recommendation:** Mark as False Positive / Meta-Reference.

### 3. Timestamp Usage in API Routes

**Files:**

- `v13/ATLAS/src/api/routes/secure_chat.py`
- `v13/ATLAS/src/core/transaction_processor.py`

**Issue:** `datetime.now(timezone.utc)` used to stamp incoming requests.
**Recommendation:**

1. Prefer client-signed timestamps (`DRV_Packet.timestamp`).
2. If server-side stamping is required (processing time), ensure it is not used for *Consensus* ordering without a logical clock. Note: QFS invariants allow "event timestamps passed explicitly".

## High Severity (Wall Clock)

### 1. UI Display Timestamps

**Files:**

- `v13/ATLAS/examples/websocket/frontend.tsx`
- `v13/ATLAS/src/components/DistributedFeed.tsx`

**Issue:** `new Date(timestamp)`.
**Recommendation:** Safe to ignore for *display* of data, providing the source data is deterministic.

### 2. Quantum Engine (Residual)

**Files:**

- `v13/ATLAS/src/core/quantum_engine.py` (Check if imports were fully removed - Fix applied).

## Next Steps

- [ ] Whitelist `randomUUID` for client-side optimistic IDs if confirmed safe.
- [ ] Whitelist audit scripts.
- [ ] Refactor API routes to `request.timestamp` preference.
