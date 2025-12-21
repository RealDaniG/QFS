# v19 Deterministic Platform Expansion

## 1. v19 Strategic Objective

**v19 is a foundation and stabilization release, not a feature sprint.**

The primary objective is to consolidate the architectural learnings from v18 into a stable, deterministic substrate for the QFS × ATLAS platform. This release prioritizes structural integrity over new user-facing features. It addresses critical gaps in authentication, P2P networking, and the desktop runtime environment to prepare the system for future multi-node scaling without enabling it prematurely.

**Key Goals:**

- **Fix v18 Architectural Gaps:** Resolve outstanding issues in authentication flows and API consistency.
- **Deterministic P2P Foundation:** Implement a verified, deterministic message envelope system for Spaces, Secure Chat, and DMs.
- **Wallet-Anchored Identity:** Ensure all system actions are cryptographically bound to the user's wallet.
- **Desktop-First Execution:** Solidify the Single-Node Local Model using Electron as the canonical runtime.
- **Preparation for Scale:** Establish the cryptographic and architectural patterns required for future multi-node features.

## 2. Scope: What v19 Covers

### Environment & Runtime (Carried Forward)

- **Environment Verification:** Scripts to validate dependencies and configuration (`.env.local` checks).
- **Backend Integrity:** Local Python backend (FastAPI) spawning key health checks and port standardization (Port 8000).
- **Electron Architecture:** Main process management, secure IPC, and static export compatibility.
- **EvidenceBus:** The immutable, SQLite-based local log for all user actions.
- **Invite System:** Deterministic, HMAC-based gating for beta access.

### Critical Gaps Resolved in v19

- **Auth Correctness:** End-to-end wallet authentication flow, ensuring session tokens are consistently derived and verified.
- **Static Export & Electron:** Full compatibility with Next.js static exports (`output: 'export'`), removing reliance on dynamic server-side rendering where incompatible with Electron.
- **Configuration Validation:** Strict validation of environment variables at startup (e.g., WalletConnect Project IDs) to prevent silent failures.

## 3. Deterministic P2P Communications

**Scope:**
P2P in v19 is strictly limited to **Spaces**, **Secure Chat**, and **Direct Messages (DMs)**. It does **not** cover global consensus, token transfers, or distributed ledger state.

**Design Principles:**

- **Deterministic Envelopes:** All messages follow a strict, canonical serialization format to ensure identical hashes across different languages and platforms.
- **Wallet-Anchored Identity:** Sender identity is exclusively defined by their wallet public key.
- **Session-Scoped Keys:** Symmetric encryption keys are ephemeral and derived deterministically from the session context (Wallet + Space + Nonce), ensuring forward secrecy and easy re-keying.
- **No Timestamps:** Message ordering and uniqueness rely on monotonic sequence counters (`client_seq`) and cryptographic hashes, avoiding non-deterministic timestamp reliance.
- **EvidenceBus as Spine:** P2P is the transport; EvidenceBus is the source of truth.

## 4. EvidenceBus as Spine

**"P2P is how information moves. EvidenceBus is what actually happened."**

- **Transport vs. Truth:** P2P envelopes are ephemeral carriers of intent. They are not the ledger.
- **Commitment:** A message is only "real" once its cryptographic hash and metadata are committed to the local EvidenceBus.
- **Replayability:** The EvidenceBus log allows the application state to be fully reconstructed deterministically, regardless of network conditions during the original transmission.

## 5. Testing & Exit Criteria

**Mandatory v19 Exit Checklists:**

### Auth E2E

- [ ] Wallet connection succeeds (Metamask/WalletConnect).
- [ ] Challenge signing works correctly.
- [ ] Session token is generated and accepted by the backend.
- [ ] Protected API routes accept the session token.

### P2P Determinism

- [ ] Cross-Language Parity: Python backend and TypeScript frontend must produce identical ciphertexts for the same inputs (Key, Nonce, AD, Plaintext).
- [ ] **Standardized Ascon**: Ascon-128, **SHA3-256** hashing, and **Empty AD** (`b""`/`undefined`) for interoperability.
- [ ] Envelope serialization ensures matching hashes in both environments.

### Electron Packaging

- [ ] `npm run build` produces a valid static export.
- [ ] `npm run build:win` (or platform equivalent) generates a launchable executable.
- [ ] Application boots, spawns backend, and renders dashboard without console errors.

### Post-Build

- [ ] Verify no secrets are bundled in the executable.
- [ ] Confirm "read-only" fallback behavior if backend connectivity fails.

## 6. Non-Claims

- **No Full PQC:** while the architecture accommodates Post-Quantum Cryptography (MOCKQPC placeholders), standard ECC is used for v19.
- **No Decentralization:** The system runs as a single-node local model. Networked federation is a future milestone.
- **No Final Topology:** The P2P discovery and routing mechanisms are provisional.
- **No Mainnet:** This is a testnet/beta release only.
