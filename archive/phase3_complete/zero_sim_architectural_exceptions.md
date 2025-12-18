# Zero-Sim Architectural Exceptions

The following patterns are whitelisted from Zero-Simulation violation checks as they represent benign infrastructure patterns that do not compromise deterministic execution.

## 1. Lazy Constant Initialization

**Pattern**: assigning to `func._cached`
**Context**: `v13/libs/CertifiedMath.py`
**Reason**: Performance optimization for BigNum128 constants. Values are hardcoded and immutable after load.
**Risk**: Low.

## 2. Dataclass Post-Initialization

**Pattern**: Assignments in `__post_init__`
**Context**: `v13/core/TokenStateBundle.py`
**Reason**: Standard Python dataclass lifecycle. Used for default value validation.
**Risk**: Low.

## 3. Keystore Loading

**Pattern**: Assignments in `_load`
**Context**: `v13/libs/keystore/manager.py`
**Reason**: Loading initial state from disk. Part of object construction.
**Risk**: Low.

## 4. Test Harness State

**Pattern**: Assignments to `self.*` in tests
**Context**: `v13/tests/`
**Reason**: Tests require state setup and teardown. Not production logic.
**Risk**: Low (Test only).
