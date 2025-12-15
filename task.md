# QFS x ATLAS V1.0 — PRODUCTION READINESS ROADMAP

## Executive Summary

This document tracks the critical path to V1.0 release. It replaces previous trackers with a comprehensive, dependency-ordered "Production Readiness" plan.

**Status Legend:**

- 🔴 **BLOCKER** - Must complete before moving forward
- 🟡 **CRITICAL** - Core functionality, high priority
- 🟢 **ENHANCEMENT** - Improves UX/security but not blocking
- 🔵 **FUTURE** - Post-V1 but plan for it now
- ✅ **DONE** - Already implemented (from repo scan)
- ⚠️ **NEEDS AUDIT** - Exists but requires review

---

## PHASE 0: FOUNDATION (Critical Path Blockers)

### F-001: Core Infrastructure Setup

**Status:** 🔴 BLOCKER

- [ ] F-001.1: Finalize repository structure (consolidate `src/` vs `v13/`). (Partially Done: Legacy src audit complete)
- [ ] F-001.2: Set up environment configs (dev/staging/prod).
- [ ] F-001.3: Configure CI/CD for ATLAS deployment (separate from QFS).
- [ ] F-001.4: Set up monitoring/logging infrastructure (Sentry, DataDog, etc.).
- [ ] F-001.5: Create deployment scripts for ATLAS frontend + backend.
- [ ] F-001.6: Set up PostgreSQL + Redis instances (staging + prod).
- [ ] F-001.7: Finalize Production Domain (Replace placeholders).

### F-002: Empty Core Files Resolution

**Status:** 🔴 BLOCKER

- [x] F-002.1: Audit `src/core/TokenStateBundle.py` (Confirmed empty placeholder).
- [x] F-002.2: Decide: Delete legacy `src/` or populate with v13 aliases? (Deleted).
- [ ] F-002.3: Document canonical code locations in CONTRIBUTING.md.
- [ ] F-002.4: Update all imports to point to correct modules. (Initial grep done, deeper check needed).
- [ ] F-002.5: Run full test suite to confirm no broken imports.

### F-003: ATLAS API Contract Specification (ATLAS-P0-001)

**Status:** 🔴 BLOCKER

- [x] F-003.1: Define REST API structure for ATLAS ↔ QFS bridge.
  - [x] `POST /v1/auth/connect-wallet` (User registration).
  - [x] `GET /v1/users/{wallet}` (User profile).
  - [x] `POST /v1/genesis/log` (Genesis Ledger append).
  - [x] `GET /v1/coherence/{wallet}` (Coherence score query).
- [x] F-003.2: Create OpenAPI/Swagger spec file (`v13/ATLAS/specs/atlas-qfs-api-v1.yaml`).
- [ ] F-003.3: Generate API client libraries (TypeScript for frontend).
- [ ] F-003.4: Write integration tests for each endpoint.
- [ ] F-003.5: Document authentication flow (wallet signature verification).

### F-004: Genesis Ledger Implementation

**Status:** 🔴 BLOCKER

- [x] F-004.1: Design Genesis Ledger schema.
- [x] F-004.2: Implement append-only ledger in PostgreSQL. (Implemented in JSONL as V1 Zero-Sim preference)
- [x] F-004.3: Create Python service (`v13/ledger/genesis_ledger.py`).
- [x] F-004.4: Implement hash chain verification.
- [x] F-004.5: Add ledger export to JSONL (Native format).
- [x] F-004.6: Write replay verification script.
- [ ] F-004.7: Add ledger backup to S3/IPFS daily.

### F-005: Event Bridge Architecture (ATLAS-P0-003)

**Status:** 🔴 BLOCKER

- [x] F-005.1: Design event bridge pattern (Message Queue vs Direct API).
- [x] F-005.2: Decide on tech: Redis Streams (Implemented with fallback).
- [x] F-005.3: Implement event publisher in ATLAS backend (`v13/integrations/event_bridge.py`).
- [ ] F-005.4: Implement Genesis Ledger subscriber.
- [x] F-005.5: Add event replay capability.
- [ ] F-005.6: Add monitoring for event lag/failures.
- [ ] F-005.7: Write event bridge integration tests.

---

## PHASE 1: CORE SECURITY

### S-001: SecureMessageV2 Security Audit

**Status:** ⚠️ NEEDS AUDIT

- [ ] S-001.1: Code review `SecureMessageV2` implementation.
- [ ] S-001.2: Verify encryption primitives (libsodium / Web Crypto API).
- [ ] S-001.3: Test key derivation from wallet signatures.
- [ ] S-001.4: Penetration test: message interception scenarios.
- [ ] S-001.5: Penetration test: replay attack vectors.
- [ ] S-001.6: Verify sequence enforcement prevents reordering.
- [ ] S-001.7: Document security assumptions in `SECURITY.md`.
- [ ] S-001.8: Create threat model diagram.

### S-002: Wallet Authentication Flow

**Status:** 🟡 CRITICAL

- [ ] S-002.1: Implement wallet signature challenge-response.
- [ ] S-002.2: Implement session token generation (JWT).
- [ ] S-002.3: Add wallet signature verification library.
- [ ] S-002.4: Handle multi-chain wallets.
- [ ] S-002.5: Add wallet-switching detection.
- [ ] S-002.6: Implement session expiration + refresh.
- [ ] S-002.7: Rate-limit auth endpoints.

### S-003: Message Encryption Implementation

**Status:** 🟡 CRITICAL

- [ ] S-003.1: Implement client-side encryption.
- [ ] S-003.2: Key exchange protocol (ECDH or wallet-derived keys).
- [ ] S-003.3: Store only ciphertext + metadata on server.
- [ ] S-003.4: Implement decryption on recipient client.
- [ ] S-003.5: Handle key rotation.
- [ ] S-003.6: Add "message delivered" vs "message read" indicators (encrypted).
- [ ] S-003.7: Test with multiple devices per wallet.

### S-004: AEGIS Service Deployment (ATLAS-P1-009)

**Status:** 🟡 CRITICAL

- [ ] S-004.1: Review AEGIS staging deployment.
- [ ] S-004.2: Configure production environment variables.
- [ ] S-004.3: Set up SSL certificates.
- [ ] S-004.4: Deploy to production server.
- [ ] S-004.5: Configure firewall rules.
- [ ] S-004.6: Implement health check endpoint.
- [ ] S-004.7: Set up uptime monitoring.
- [ ] S-004.8: Load test AEGIS.
- [ ] S-004.9: Document AEGIS API usage in ATLAS.

---

## PHASE 2: CORE FEATURES (V1 MVP)

### C-001: Wallet Connection UI

**Status:** 🟡 CRITICAL

- [x] C-001.1: Design "Connect Wallet" button (UI/UX).
- [x] C-001.2: Implement MetaMask detection.
- [ ] C-001.3: Implement WalletConnect modal.
- [ ] C-001.4: Add "Install MetaMask" prompt for new users.
- [x] C-001.5: Show connected wallet address (truncated).
- [x] C-001.6: Add "Disconnect" functionality.
- [x] C-001.7: Handle wallet rejection errors gracefully.
- [x] C-001.8: Add loading states during connection.

### C-002: User Profile System

**Status:** 🟡 CRITICAL

- [ ] C-002.1: Design profile data schema.
- [ ] C-002.2: Create profile creation flow.
- [ ] C-002.3: Implement profile edit page.
- [ ] C-002.4: Add avatar upload.
- [ ] C-002.5: Generate unique referral code.
- [ ] C-002.6: Display coherence score + genesis points.
- [ ] C-002.7: Show referral tree.

### C-003: 1-to-1 Chat Implementation

**Status:** 🟡 CRITICAL

- [ ] C-003.1: Design chat UI.
- [ ] C-003.2: Implement WebSocket connection.
- [ ] C-003.3: Send encrypted message.
- [ ] C-003.4: Store message (ciphertext only).
- [ ] C-003.5: Emit message to recipient.
- [ ] C-003.6: Decrypt message.
- [ ] C-003.7: Display message history.
- [ ] C-003.8: Add "typing..." indicator.
- [ ] C-003.9: Message timestamps.
- [ ] C-003.10: Log to Genesis Ledger via event bridge.

### C-004: Chat Inbox / Conversations List

**Status:** 🟡 CRITICAL

- [ ] C-004.1: Design inbox UI.
- [ ] C-004.2: Show last message preview.
- [ ] C-004.3: Show unread message count.
- [ ] C-004.4: Sort conversations.
- [ ] C-004.5: Add search functionality.
- [ ] C-004.6: "Start New Chat" button.
- [ ] C-004.7: Handle empty state.

### C-005: Referral System

**Status:** 🟡 CRITICAL

- [ ] C-005.1: Generate unique referral link.
- [ ] C-005.2: Implement referral code validation.
- [ ] C-005.3: Store referrer → referee relationship.
- [ ] C-005.4: Award Genesis Points on successful referral.
