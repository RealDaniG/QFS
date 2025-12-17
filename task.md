# QFS x ATLAS V1.0 — PRODUCTION READINESS ROADMAP

**Goal:** Zero-Sim Absolute V1.0 Release (BETA v13.8)
**Status:** Phase 6 (Explain-This System)
**License:** AGPL-3.0

---

## 📅 Phase 0: Foundation (Optimized)

**Status:** ✅ COMPLETE

- [x] F-001: Core Infrastructure (Repo, CI/CD, Env).
- [x] F-002: Resolve Empty Core Files.
- [x] F-003: ATLAS API Contracts.
- [x] F-003.5: `POST /v1/events/batch` Endpoint.
- [x] F-004: Genesis Ledger (JSONL Canonical format).
- [x] F-005: Event Bridge Architecture.
- [x] F-005.X: Redis Streams Partitioning Spec.

---

## 🔒 Phase 1: Core Security (V1 Minimum)

**Status:** ✅ COMPLETE

- [x] S-001A: SecureMessageV2 (Encryption, Replay Protection).
- [x] S-002: Wallet Auth Flow (Connect, Challenge-Response).
- [x] S-002.X: Deterministic Wallet→UserID Mapper (`user_{hash}`).
- [x] S-003A: Basic E2E Encryption (No Plaintext).
- [x] S-004: AEGIS Integration (Staged).

---

## 💬 Phase 2: Core Features (Social Primitives)

**Status:** ✅ COMPLETE

### C-001: Wallet Connection

- [x] C-001.1: Metamask/EVM Connect.
- [x] C-001.2: Deterministic User ID derivation.

### C-002: User Profiles

- [x] C-002.1: Profile creation/storage (Ledger-backed).
- [x] C-002.2: Avatar/Bio sync.

### C-003: 1-to-1 Chat (Secure)

- [x] C-003.1: ChatWindow UI.
- [x] C-003.2: WebSocket Client (Auth).
- [x] C-003.3: E2E Encryption (Client-side).
- [x] C-003.4: Ledger Event Logging (`MESSAGE` hash).

### C-004: Chat Inbox

- [x] C-004.1: Thread listing from Ledger events.

### C-005: Referral System

- [x] C-005.1: `REFERRAL_USE` Ledger Event.
- [x] C-005.2: Backend Stats API.
- [x] C-005.3: Frontend Invite Capture.
- [x] C-005.4: Dashboard.

---

## 🔄 Phase 2.5: Trust Loop Validation (CRITICAL)

**Status:** ✅ COMPLETE

> **Objective:** Prove the "Minimal Trust Loop" works end-to-end.
> Flow: Wallet → Profile → Chat → Referral → Reward → Coherence.

- [x] **L-001: End-to-End Walkthrough Script**
  - [x] Create `v13/scripts/verify_trust_loop.py` (Automated User Journey).
  - [x] Simulate Alice invites Bob.
  - [x] Bob connects, system logs Referral.
  - [x] Alice & Bob chat (Encrypted).
  - [x] Reward triggers (Coherence update).
  - [x] Verify Ledger for all 3 event types (`LOGIN`, `REFERRAL_USE`, `MESSAGE`).
  - [x] **Verified** (Script passing).

- [x] **L-002: Coherence Closing Loop**
  - [x] Ensure Referral actually increments Genesis Points/Coherence in `ValueNode`.
  - [x] Verify `GET /profile` reflects new score immediately after loop.

---

## 🧠 Phase 6: Explain-This System (Transparency)

**Status:** 🟡 IN PROGRESS

- [x] E-001: `GET /explain/reward/{tx_id}` endpoint.
- [ ] E-002: Frontend "Why did I get this?" tooltip.
- [x] E-003: Cryptographic Proof extraction (CLI Tool).

## 🛡️ Phase 7: Session Management System

**Status:** ✅ COMPLETE

- [x] Deterministic session layer with challenge-response authentication
- [x] Ledger-replayable session state
- [x] Explain-This integration for session proofs
- [x] Zero-Simulation compliance
- [x] Comprehensive test coverage (17 tests)

---

## 🚀 Phase X: Deployment & Hardening

- [ ] D-001: Production Env Config.
- [ ] D-002: Load Testing (Chat Socket).
- [ ] D-003: Sentry/Monitoring (Post-V1).

## 🔄 Phase 18.9: QFS v18.9 Release

**Status:** 🟡 PLANNED

- [ ] Update to QFS v18.9
- [ ] GitHub tag and release
- [ ] Full documentation update
- [ ] Repository push to main branch

## 🛠️ Infrastructure Fixes (Ongoing)

- [x] CI: Upgrade `upload-artifact` to v4.
- [x] Security: Remove Hash Truncation.
- [x] CI: Fix `AST_ZeroSimChecker.py` path (src vs v13).
- [x] Docs: Document PQC backend strategy & production requirements.
