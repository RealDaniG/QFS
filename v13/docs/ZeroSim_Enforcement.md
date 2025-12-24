# Zero-Sim Enforcement Policy (v13.5)

> **Philosophy**: A distributed ledger cannot reach consensus if nodes behave differently based on local time, floating point hardware deviations, or random seeds.

## 1. The Rules

1. **NO `import random`**: Use `CertifiedMath` PRNG seeded by block hash.
2. **NO `import time`**: Use block timestamps passed into the function.
3. **NO `float` math**: Use `BigNum128` fixed-point arithmetic.
4. **No unbounded loops**: All iteration must be bounded by a constant or gas limit.

## 2. Automated Enforcement Strategy

We employ a two-tier defense strategy:

### Tier 1: Fast CI Guardrail (`scripts/check_zero_sim.py`)

- **When**: Runs on every `push` and `PR`.
- **Scope**: Scans modified files for obvious violations (imports, float calls).
- **Action**: Fails the build immediately.

### Tier 2: Deep Static Audit (`v13/tools/AST_zero_sim_checker.py`)

- **When**: Run nightly or manually before major core refactors.
- **Scope**: Full AST traversal, complexity analysis, and heuristic checks for non-deterministic behavior.
- **Action**: Generates a detailed compliance report.

## 3. How to Run Locally

**Fast Check**:

```bash
python scripts/check_zero_sim.py
```

**Deep Audit**:

```bash
python v13/tools/AST_zero_sim_checker.py
```

## 4. Exclusions

Tests, scripts, and mock files are excluded from strict enforcement to allow for test orchestration and data generation.

## 5. Allowed Patterns

| Forbidden | Allowed |
| :--- | :--- |
| `time.time()` | `token_bundle.timestamp` |
| `random.randint()` | `utils.deterministic_rng(seed)` |
| `3.14159` | `BigNum128.from_float(3.14159)` (Import/Convert only) |
