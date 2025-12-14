# Zero-Simulation QFS × ATLAS Contract (v1.2)

> **Authority:** This document supersedes all local slice-level configuration.
> **Enforcement:** Verified by `run_zero_sim_suite.py` and strictly enforced by CI.

## 1. The Prime Invariant: Economic Truth

**QFS is the sole source of economic truth.**

- **No ATLAS Mutation:** The ATLAS frontend, API, and database layers **must never** directly mutate balances, mint tokens, or issue rewards.
- **Read-Only Projections:** All values displayed in ATLAS (Wallet, Profile, Feed) must be derived from a **read-only replay** of QFS ledger events.
- **Intent-Only Writes:** ATLAS may only submit **signed intents** (DRV packets) to the QFS consensus layer (or AEGIS API).

## 2. Zero-Simulation Compliance (System-Wide)

Every component in the critical path (Logic → Economics → Explanation) must adhere to:

### 2.1 No Randomness

- **Forbidden:** `random.random()`, `uuid.uuid4()`, `os.urandom()` (outside of keygen).
- **Allowed:** Deterministic PRNG seeded by ledger state or content hash.

### 2.2 No Wall-Clock Time

- **Forbidden:** `time.time()`, `datetime.now()`, `new Date()`.
- **Allowed:** `DRV_Packet.timestamp` (ledger time), `block_height`, or event timestamps passed explicitly.

### 2.3 No Floating Point Economics

- **Forbidden:** `float`, `double` for any token/value calculation.
- **Allowed:** `BigNum128`, integer-based fixed-point arithmetic.

## 3. Slice-Level Invariants

### 3.1 Humor / Signal Slices

- **Pure Signals:** SignalAddons must emit `SignalResult` only. They cannot trigger payouts directly.
- **Replayability:** A signal score must be reproducible given the same `(Content, Context, Policy)` tuple.

### 3.2 Value Nodes

- **Derived State:** A Value Node's state is a pure function of `Σ(Events)`.
- **Reference Graph:** The `ValueGraphRef` must be constructible from the event log without external database queries.

### 3.3 Storage Engine

- **Content Addressing:** All content is referenced by immutable hash (CID).
- **Proof Replay:** Storage proofs must be verifiable against the QFS ledger history.

## 4. Explanation & Transparency

**"If you can't explain it via replay, you can't show it."**

- **Explanation Hash:** Every `/explain/*` response must include a SHA-256 hash of the explanation object.
- **Policy Versioning:** Explanations must cite the specific Policy ID/Hash used to derive the result.
- **Stub-Free:** Mocks are permitted for *testing* only. Production endpoints must use `QFSReplaySource`.

## 5. Implementation Contract

- **Language:** Python (Backend Policy), TypeScript (Frontend Types).
- **Type Safety:** Shared types must remain synchronized between `v13/policy/*.py` and `v13/ATLAS/src/lib/qfs/*.ts`.
- **Testing:** `run_zero_sim_suite.py` must pass green before any deployment.
