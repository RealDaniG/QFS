# Batch 5 Pre-Analysis: GLOBAL_MUTATION Violations

## Sample Analysis (50 violations examined)

### Pattern Categories Identified

#### 1. **`__all__` Exports** (SAFE TO KEEP)

**Count:** ~15 violations  
**Pattern:** `__all__ = [...]`  
**Examples:**

```python
v13/AEGIS/__init__.py:25 [GLOBAL_MUTATION] Global assignment to '__all__' forbidden
v13/AEGIS/governance/__init__.py:8 [GLOBAL_MUTATION] Global assignment to '__all__' forbidden
```

**Decision:** **DO NOT TRANSFORM**  
**Reason:** `__all__` is a Python convention for module exports. Removing it would break imports.

---

#### 2. **Version Strings** (SAFE TO KEEP)

**Count:** ~5 violations  
**Pattern:** `__version__ = "..."`  
**Examples:**

```python
v13/AEGIS/__init__.py:15 [GLOBAL_MUTATION] Global assignment to '__version__' forbidden
v13/AEGIS/__init__.py:16 [GLOBAL_MUTATION] Global assignment to '__contract_version__' forbidden
```

**Decision:** **DO NOT TRANSFORM**  
**Reason:** Version strings are metadata, not mutable state. Standard Python practice.

---

#### 3. **Pydantic `json_schema_extra`** (SAFE TO KEEP)

**Count:** ~10 violations  
**Pattern:** `json_schema_extra = {...}` in Pydantic models  
**Examples:**

```python
v13/AEGIS/governance/proposals.py:40 [GLOBAL_MUTATION] Global assignment to 'json_schema_extra' forbidden
v13/AEGIS/ui_contracts/schemas.py:38 [GLOBAL_MUTATION] Global assignment to 'json_schema_extra' forbidden
```

**Decision:** **DO NOT TRANSFORM**  
**Reason:** Pydantic configuration, not runtime mutation. Framework requirement.

---

#### 4. **Module-Level Singletons** (CANDIDATES FOR TRANSFORMATION)

**Count:** ~5 violations  
**Pattern:** `logger = ...`, `router = ...`, `cm = ...`  
**Examples:**

```python
v13/core/observability/logger.py:121 [GLOBAL_MUTATION] Global assignment to 'logger' forbidden
v13/AEGIS/services/governance_map.py:27 [GLOBAL_MUTATION] Global assignment to 'router' forbidden
v13/libs/BigNum128.py:21 [GLOBAL_MUTATION] Global assignment to 'cm' forbidden
```

**Decision:** **TRANSFORM TO FACTORY FUNCTIONS**  
**Reason:** These can be lazily initialized or moved to function scope.

**Transformation:**

```python
# Before
logger = StructuredLogger()

# After
def get_logger():
    global _logger
    if '_logger' not in globals():
        _logger = StructuredLogger()
    return _logger
```

---

#### 5. **Type Aliases** (SAFE TO KEEP)

**Count:** ~2 violations  
**Pattern:** `TypeName = Any`  
**Examples:**

```python
v13/core/CoherenceEngine.py:19 [GLOBAL_MUTATION] Global assignment to 'ReferralRewarded' forbidden
```

**Decision:** **DO NOT TRANSFORM**  
**Reason:** Type aliases are compile-time, not runtime mutations.

---

## Transformation Strategy

### Safe Targets (Transform These)

**Estimated:** 5-10 violations  
**Pattern:** Module-level singletons (logger, router, etc.)

**Approach:**

1. Convert to lazy initialization functions
2. Use module-level `_private` variables
3. Provide `get_X()` factory functions

### Excluded Patterns (Do NOT Transform)

- `__all__` exports (~15)
- `__version__` strings (~5)
- `json_schema_extra` Pydantic config (~10)
- Type aliases (~2)

**Total Excluded:** ~32 violations

---

## Expected Impact

**Total GLOBAL_MUTATION violations:** ~250 (estimated)  
**Safe to transform:** ~10-20 violations  
**Expected reduction:** **10-20 violations** (4-8%)

**⚠️ WARNING:** This batch will have **minimal impact** because most GLOBAL_MUTATION violations are legitimate Python patterns that should NOT be transformed.

---

## Recommendation

### Option A: Skip Batch 5 (RECOMMENDED)

**Reason:** Only 10-20 transformable violations out of ~250 total. Not worth the risk for minimal gain.

**Action:** Move directly to next high-impact batch.

### Option B: Transform Only Singletons

**Reason:** Safe, small scope, low risk.

**Action:** Transform 5-10 logger/router singletons to factory functions.

**Expected:** -10 to -20 violations

### Option C: Request AST Checker Update

**Reason:** Checker should exclude legitimate patterns like `__all__`, `__version__`, `json_schema_extra`.

**Action:** Update checker exclusion rules, re-measure baseline.

---

## Decision Required

**Which option do you prefer?**

1. **Option A:** Skip Batch 5, move to next batch
2. **Option B:** Transform only singletons (minimal impact)
3. **Option C:** Update checker to exclude legitimate patterns

**My Recommendation:** **Option C** → Update checker, then reassess remaining violations.

---

*Analysis Date: 2025-12-17T20:57:00Z*  
*Samples Analyzed: 50 violations*  
*Safe Targets: 5-10 violations*
