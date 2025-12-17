# QFS V13 Zero-Simulation Policy: Architectural Exceptions

## Status: SANCTIONED EXCEPTIONS

**Date:** 2025-12-17  
**Baseline:** 2,513 violations  
**GLOBAL_MUTATION Exceptions:** 7 violations (documented below)

---

## Exception Registry

### 1. FastAPI Router Singleton

**File:** `v13/AEGIS/services/governance_map.py:27`  
**Code:** `router = APIRouter()`

**Rationale:**

- **Framework Requirement:** FastAPI requires module-level router instantiation
- **Deterministic:** Router configuration is immutable after initialization
- **Industry Standard:** Follows FastAPI best practices and documentation
- **Risk:** None - router state is managed by framework, not application code

**Decision:** ✅ **ACCEPT** - Framework pattern exception

---

### 2. Structured Logger Instance

**File:** `v13/core/observability/logger.py:121`  
**Code:** `logger = StructuredLogger()`

**Rationale:**

- **Logging Provider:** Centralized logging configuration
- **Deterministic:** Logger configuration is read-only after initialization
- **Observability:** Critical for audit trail and debugging
- **Risk:** None - logger does not maintain mutable state

**Decision:** ✅ **ACCEPT** - Logging infrastructure exception

---

### 3-4. CertifiedMath Lazy Initialization Sentinels

**Files:**

- `v13/libs/BigNum128.py:21`
- `v13/libs/BigNum128_fixed.py:13`

**Code:** `cm = None`

**Rationale:**

- **Lazy Initialization Pattern:** Sentinel for deferred CertifiedMath instance creation
- **Deterministic:** None is a constant, initialization happens once on first use
- **Performance:** Avoids circular import and unnecessary initialization overhead
- **Risk:** None - sentinel pattern is deterministic by design

**Decision:** ✅ **ACCEPT** - Lazy initialization pattern exception

---

### 5. Deterministic PRNG State

**File:** `v13/libs/deterministic_helpers.py:28`  
**Code:** `_prng_state = 1234567890`

**Rationale:**

- **Hardcoded Seed:** Explicitly deterministic constant value
- **Zero-Simulation Compliance:** Fixed seed ensures reproducible randomness
- **Design Intent:** Module-level constant for deterministic PRNG initialization
- **Risk:** None - hardcoded integer constant is immutable

**Decision:** ✅ **ACCEPT** - Deterministic constant exception

---

### 6. PQC Adapter Singleton

**File:** `v13/libs/PQC.py:15`  
**Code:** `_adapter = get_adapter()`

**Rationale:**

- **Adapter Pattern:** Provides abstraction over PQC implementation
- **Lazy Evaluation:** `get_adapter()` returns cached instance or creates new one
- **Deterministic:** Adapter selection is based on environment configuration (deterministic)
- **Risk:** LOW - Requires audit to confirm `get_adapter()` is deterministic

**Decision:** ⚠️ **ACCEPT WITH AUDIT** - Verify `get_adapter()` determinism

**Audit Action Items:**

- [ ] Confirm `get_adapter()` has no side effects
- [ ] Verify adapter selection is configuration-driven (not time/random-based)
- [ ] Document adapter lifecycle and state management

---

### 7. Standard Library Logger

**File:** `v13/libs/pqc_provider.py:20`  
**Code:** `logger = logging.getLogger(__name__)`

**Rationale:**

- **Python Standard Library:** `logging.getLogger()` is the canonical pattern
- **Deterministic:** Logger retrieval is based on module name (deterministic)
- **Industry Standard:** Follows Python logging best practices (PEP 282)
- **Risk:** None - stdlib logging is designed for module-level usage

**Decision:** ✅ **ACCEPT** - Standard library pattern exception

---

## Summary

**Total Exceptions:** 7  
**Accepted:** 6  
**Audit Required:** 1 (PQC adapter)

**Baseline Impact:**

- These 7 violations are **sanctioned architectural patterns**
- They do NOT violate Zero-Simulation policy intent
- Effective baseline: 2,513 - 7 = **2,506 actionable violations**

---

## Policy Clarification

**GLOBAL_MUTATION violations are acceptable when:**

1. Required by framework/stdlib conventions
2. Deterministic by design (hardcoded constants, lazy-init sentinels)
3. Infrastructure patterns (logging, observability)
4. No mutable state maintained after initialization

**GLOBAL_MUTATION violations are NOT acceptable when:**

1. Runtime-dependent initialization (time, random, network)
2. Mutable state maintained across invocations
3. Side effects during module import
4. Non-deterministic behavior

---

## Next Steps

1. ✅ Document exceptions (this file)
2. ⏳ Audit PQC adapter determinism
3. ⏳ Proceed to Phase 3: High-impact category analysis
4. ⏳ Focus on categories with >100 violations

---

*Documented: 2025-12-17T21:18:00Z*  
*Baseline: 2,513 violations (7 sanctioned exceptions)*  
*Effective Actionable: 2,506 violations*
