# Phase 2 Transformation Guide

## Manual Transformations Required

Due to the complexity and context-specific nature of singleton patterns,
these transformations should be done manually with careful consideration.

## Transformation Pattern

### Before (Module-level singleton):
```python
logger = StructuredLogger()
```

### After (Lazy-initialized factory):
```python
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        _logger = StructuredLogger()
    return _logger
```

## Files to Transform


### v13\AEGIS\services\governance_map.py
**Line 27:** `router`
```python
router = APIRouter()
```

### v13\core\CoherenceEngine.py
**Line 19:** `ReferralRewarded`
```python
ReferralRewarded = Any
```

### v13\core\observability\logger.py
**Line 121:** `logger`
```python
logger = StructuredLogger()
```

### v13\libs\BigNum128.py
**Line 21:** `cm`
```python
cm = None
```

### v13\libs\BigNum128_fixed.py
**Line 13:** `cm`
```python
cm = None
```

### v13\libs\deterministic_helpers.py
**Line 28:** `_prng_state`
```python
_prng_state = 1234567890
```

### v13\libs\PQC.py
**Line 15:** `_adapter`
```python
_adapter = get_adapter()
```

### v13\libs\pqc_provider.py
**Line 20:** `logger`
```python
logger = logging.getLogger(__name__)
```

## Verification Steps

1. Make changes manually to each file
2. Run: `python v13/libs/AST_ZeroSimChecker.py v13/ --fail`
3. Verify GLOBAL_MUTATION count drops to 0
4. Run tests: `pytest v13/tests/ -v`
5. Commit if successful

## Safety

- Each transformation is reversible via git
- Test after each file transformation
- If tests fail, revert that file and skip it
