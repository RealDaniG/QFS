# Strategy: Phase 6 - Layer 3 Deep Dives & Complex Remediation

**Status:** Planning
**Target:** 3,850 -> 0 Violations
**Timeline:** Weeks 3-12

## Objective

Address "Hard" violations requiring semantic understanding, logic refactoring, or state management changes.

## Violation Categories (Layer 3)

### 1. Complex Float Literals (Category C)

* **Problem:** Scientific constants (`3.14159`), calibration coefficients (`0.333...`), and sensitive financial constants.
* **Strategy:**
  * **Scientific:** Replace with `math.pi`, `math.e`.
  * **Coefficients:** Convert to `Fraction` where rational, or wrap in `CertifiedMath.coefficient()`.
  * **Financial:** strict review; convert to `Decimal` or `Fraction` inside `QuantumCurrency` types.

### 2. Mutation & State (MUTATION_ASSIGNMENT)

* **Problem:** In-place variations (`x += 1`, `self.state = new_state`) violating functional purity.
* **Strategy:**
  * **detect:** AST analysis of `AugAssign` and attribute assignment.
  * **Refactor:**
    * Local accumulation -> `reduce` or list comprehensions.
    * Object state -> `dataclasses.replace(obj, field=val)`.
    * Global state -> `ContextVar` or explicit threading.

### 3. Non-Deterministic Logic (CONTROL_FLOW)

* **Problem:** `random.choice`, `set` iteration (remaining complex cases).
* **Strategy:**
  * Use `DeterministicRNG` (seeded).
  * Enforce `sorted()` on all collection iteration (analyzer rule).

### 4. Function Purity (FUNCTION_STATE)

* **Problem:** Functions depending on hidden state (time, globals).
* **Strategy:** Dependency Injection (Pass `clock`, `rng` as args).

## Execution Plan

* **Batch 12:** MUTATION_ASSIGNMENT (High Volume)
* **Batch 13:** FUNCTION_STATE (High Risk)
* **Batch 14:** CONTROL_FLOW & Remaing Floats
* **Batch 15:** Final Polish & Whitelisting

## Success Metrics

* Zero-Simulation Compliance (0 Violations).
* 100% Deterministic Replay (Verified by `EntropyCheck`).
