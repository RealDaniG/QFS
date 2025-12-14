# QFS System Invariants (Zero-Sim)

This document defines the non-negotiable hard invariants for SignalAddons, Policy, and Signal vectors within the QFS ecosystem. These invariants are enforced by tests and architectural constraints.

## 1. SignalAddon Invariants

* **No Side Effects**: `evaluate()` MUST NOT mutate any global state, write to the ledger directly, or allocate rewards. It must only return a `SignalResult`.
* **Deterministic**: `evaluate(content, context)` MUST always return the exact same `SignalResult` (including hashes) for the same inputs, regardless of time of day or machine.
* **Isolation**: Addons MUST NOT depend on other Addons (no cross-addon reads).
* **No External I/O**: Addons MUST NOT make network calls (fetch, axios, etc.) to non-content-addressed storage. IPFS reads are permitted if content-addressed.

## 2. Policy Invariants

* **Global Reward Caps**: Comedy bonuses (and other addons) MUST NEVER exceed the base coherence reward. This is a UX invariant to prevent "farming" of secondary signals.
* **Gating Priority**: `CoherenceEngine` gating (base coherence score) is PRIMARY. If base coherence fails, no addon bonuses are awarded, regardless of their score.
* **Zero-Sim**: Policies define rules (weights, gates), but the *execution* of those rules happens in the QFS Node (backend). The client/treasury logic here is a *projection* or *verification* of that logic.

## 3. Signal Input Invariants

* **On-Ledger Inputs Only**: All inputs to `evaluate()` must be derived from:
    1. The content itself (immutable).
    2. The `EvalContext` which contains parameters derived strictly from the Ledger (e.g. `reputation`, `historyHash`, `derivedMetrics`).
* **Time Independence**: Do not use `Date.now()` inside logic unless it refers to a frozen timestamp passed in `EvalContext`.

## 4. AEGIS Rollback Semantics

* **Immutable History**: AEGIS CANNOT delete or rewrite `SignalEvaluated` or `RewardAllocated` events.
* **Forward Correction**: AEGIS CAN pause a policy or issue counter-balancing adjustment events.
