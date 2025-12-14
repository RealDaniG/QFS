# ATLAS V13.8 Autonomous Engineering Plan
>
> **Status:** Draft
> **Focus:** Full-Stack Determinism & Production Integration for Explain-This & StorageEngine
> **Agent:** Zero-Sim Autonomous Engineering Agent

## 🌟 North Star

Integrate ATLAS Explain-This and StorageEngine with the live QFS Ledger to achieve **100% deterministic, cryptographic auditability** of all user rewards, content rankings, and storage placement decisions, verified by the AEGIS governance layer without simulation gaps.

---

## 🔄 Cycle 1: Live Ledger Integration & Policy Time-Travel

**Focus:** Connect `QFSReplaySource` to actual ledger artifacts and enable version-correct policy replay.

### Objectives

1. **True Event Sourcing:** Replace mock/stub data in `QFSReplaySource` with actual reads from `TokenStateBundle` and `StorageEvent` logs.
2. **Policy Time-Travel:** Ensure that explaining a reward from Epoch X uses Policy Version active at Epoch X.
3. **Cross-Epoch Context:** Enable explanations that depend on history (e.g., streak bonuses).

### Key Tasks

| Component | Task | Type | Description |
|-----------|------|------|-------------|
| **Core** | `QFSReplaySource.py` | Logic | Implement `_fetch_from_live_ledger` to parse `v13/ledger/` artifacts. |
| **Policy** | `PolicyRegistry.py` | Logic | Implement `get_policy_for_epoch(epoch: int)` returning historical config. |
| **API** | `dependencies.py` | Wiring | Configure factory to inject `LiveLedgerReplaySource` in production mode. |
| **Tests** | `test_live_replay.py` | Test | Integration test verifying replay matches recorded state for 10 epochs. |

---

## 🔄 Cycle 2: Storage Integrity & AEGIS Audits

**Focus:** Verify verifiable storage proofs and integrate AEGIS identity checks into the explanation loop.

### Objectives

1. **Storage Audits:** Expose deterministic Merkle proofs for content storage via the API.
2. **AEGIS Identity:** Verify that all "active" nodes in an explanation were AEGIS-verified at that time.
3. **Visual Proofs:** Provide frontend data structures for visualizing fragment placement and redundancy.
| **Ops** | `DriftDetector.py` | Service | Background worker comparing Replay outputs vs Ledger checkpoints. |
| **CI** | `replay-drill.yml` | CI | Nightly workflow replaying entire history to verify zero divergence. |
| **UI** | `DriftDashboard.tsx` | UI | Frontend view showing divergence metrics (target: 0.00%). |
| **Manual** | `OPERATOR_GUIDE.md` | Doc | Runbooks for handling evidence mismatches or policy rollbacks. |

---

## 🛡️ Invariants & Guardrails

### 1. The "Ledger Truth" Invariant

* **Definition:** The `TokenStateBundle` is the single source of truth. Any explanation that contradicts the bundle is by definition a bug in the explainer, not the ledger.
* **Enforcement:** `assert replay_result.hash == ledger_entry.hash` in all DRILL tests.

### 2. The "Closed System" Invariant (Zero-Sim)

* **Definition:** No external API calls, clocks, or RNG allowed during the `explain()` phase.
* **Enforcement:** `ZeroMock` static analysis scanner running in CI.

### 3. The "Policy Consistency" Invariant

* **Definition:** An explanation must verify using the *hash of the policy* stored in the ledger event, not the current code version.
* **Enforcement:** `ValueNodeExplainability` must accept `policy_context` as input.

---

## 🧪 Replay Drills

### Drill A: The "Time Machine"

1. Spin up a fresh QFS instance.
2. Ingest a 10,000-event ledger from Production V13.6.
3. Ask for explanations for 50 random transactions.
4. **Assert:** All generated hashes verify against the provided ledger signatures.

### Drill B: The "Bad Actor" (Fuzzing)

1. Inject 1 corrupt event (invalid signature) into a valid ledger chain.
2. Run Replay Engine.
3. **Assert:** Engine halts or flags the specific corruption at the exact tick it occurred.

---

## 📚 Documentation Plan

1. **`v13/docs/ATLAS_EXPLAINABILITY_ARCH.md`**: Deep dive into the `QFSReplaySource` architecture.
2. **`v13/docs/STORAGE_VERIFICATION_GUIDE.md`**: How to manually verify a Merkle proof using CLI tools.
3. **`v13/docs/OPERATOR_RUNBOOK_V13.8.md`**: Guide for deploying and monitoring the V13.8 stack.
