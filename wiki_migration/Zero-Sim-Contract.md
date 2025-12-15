# Zero-Simulation Contract v1.3

> **The immutable constitution of the QFS economic engine.**

## 🔍 The Prime Invariant

**QFS is the sole source of economic truth.**
The ATLAS frontend is a read-only projection loop. It never mutates state directly. All changes originate from signed intents processed by the deterministic QFS ledger.

## 🚫 The "Zero" Rules

To ensure absolute determinism and replayability, the following are STRICTLY FORBIDDEN in the economic core:

1. **Zero Randomness:** No `random()`, `uuid4()`, or non-deterministic entropy. All randomness must be seeded by ledger state hashes.
2. **Zero Wall-Clock:** No `time.time()` or system clocks. Time is discrete (block height / epoch).
3. **Zero Floats:** No floating point math for token values. Use `BigNum128` or integer scaling only.
4. **Zero External I/O:** No network calls or DB reads in the consensus loop. Logic must be pure.
5. **Zero Hidden State:** No mutable globals or singletons.

## 🛡️ Integration Verification

Compliance is enforced by:

* **Static Analysis:** `AST_ZeroSimChecker.py` scans code for forbidden calls.
* **Replay Tests:** Nightly verification that `Replay(Events) == State`.
* **CI Gates:** Build fails if any violation is detected.

## 📖 Full Specification

[Read the complete Zero-Sim Contract v1.3](https://github.com/RealDaniG/QFS/blob/main/v13/docs/ZERO_SIM_QFS_ATLAS_CONTRACT.md)
