# QFS x ATLAS V1.0 — PRODUCTION READINESS ROADMAP

**Goal:** Zero-Sim Absolute V1.0 Release (BETA v13.8)
**Status:** Phase 2.5 (Trust Loop Validation)
**License:** AGPL-3.0

---

## 📅 Phase 0: Foundation (Optimized)

**Status:** ✅ COMPLETE

- [x] F-001: Core Infrastructure (Repo, CI/CD, Env).
- [x] F-002: Resolve Empty Core Files.
- [x] F-003: ATLAS API Contracts.
- [x] F-004: Genesis Ledger (JSONL Canonical format).
- [x] F-005: Event Bridge Architecture.

---

## 🔒 Phase 1: Core Security (V1 Minimum)

**Status:** ✅ COMPLETE

- [x] S-001A: SecureMessageV2 (Encryption, Replay Protection).
- [x] S-002: Wallet Auth Flow (Connect, Challenge-Response).
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

**Status:** 🟡 PENDING

> **Objective:** Prove the "Minimal Trust Loop" works end-to-end.
> Flow: Wallet → Profile → Chat → Referral → Reward → Coherence.

- [ ] **L-001: End-to-End Walkthrough Script**
  - [ ] Create `v13/scripts/verify_trust_loop.py` (Automated User Journey).
  - [ ] Simulate Alice invites Bob.
  - [ ] Bob connects, system logs Referral.
  - [ ] Alice & Bob chat (Encrypted).
  - [ ] Reward triggers (Coherence update).
  - [ ] Verify Ledger for all 3 event types (`LOGIN`, `REFERRAL_USE`, `MESSAGE`).

- [ ] **L-002: Coherence Closing Loop**
  - [ ] Ensure Referral actually increments Genesis Points/Coherence in `ValueNode`.
  - [ ] Verify `GET /profile` reflects new score immediately after loop.

---

## 🧠 Phase 6: Explain-This System (Transparency)

**Status:** ⚪ PENDING

- [ ] E-001: `GET /explain/reward/{tx_id}` endpoint.
- [ ] E-002: Frontend "Why did I get this?" tooltip.
- [ ] E-003: Cryptographic Proof extraction.

---

## 🚀 Phase X: Deployment & Hardening

- [ ] D-001: Production Env Config.
- [ ] D-002: Load Testing (Chat Socket).
- [ ] D-003: Sentry/Monitoring (Post-V1).
