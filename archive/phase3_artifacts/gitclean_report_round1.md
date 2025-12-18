# GITCLEAN Report Round 1

**Branch:** `fix/gitclean-ci`
**Date:** 2025-12-17

## Failed Jobs (Local Simulation)

### 1. Zero-Simulation Compliance (AST Checker)

* **Failed File**: `v13/ledger/genesis_ledger.py`
  * **Error**: Usage of `datetime.utcnow().timestamp()` / `datetime.now`.
  * **Violation**: Non-deterministic time source in core ledger logic.
* **Suspected File**: `v13/libs/logging/__init__.py`? (Need verification)

### 2. Unit Tests / Imports

* **Error**: `ImportError: No module named 'aes256_ctr_drbg'`
  * **Impact**: PQC libraries falling back to weak RNG or failing.
* **Error**: `Prohibited built-in usage: float` in `v13/ATLAS/src/signals/test_humor.py` (or similar).

## Root Causes

* Core `genesis_ledger` using system time instead of `det_time_isoformat` or equivalent.
* Missing optional dependency `aes256_ctr_drbg` in environment (Warning only? Or Failure?).
* Tests using prohibited types (`float`) in strict modules.

## Plan

1. Fix `genesis_ledger.py` to use deterministic time source (or `int(time.time())` if outside simulation strictness, but AST flagged it).
2. Inspect `aes256_ctr_drbg` issue - likely safe to ignore if fallback exists, but should silence warning if possible.
3. Fix `float` usage if in strict file.
