# QFS × ATLAS Auth Integration Roadmap (v18 → v21)

**Context:** QFS repository is at v20 (ALPHA V15.5) with active development toward v21. This roadmap aligns authentication with the ATLAS×QFS roadmap and the v20 alignment requirements.

## Phase v18 – Auth Core Expansion

**Goal:** Centralize auth, formalize sessions, plug into EvidenceBus, and prepare MOCKPQC/device slots without changing UX.

### AuthService Consolidation

- [ ] Identify all current auth codepaths (backend routes, helpers, IPC handlers).
- [ ] Introduce `AuthService` module/class as the only entry for:
  - `verifyWalletLogin(nonce, signature)`.
  - `createSession(subjects, deviceHash)`.
  - `refreshSession(refreshToken, deviceHash)`.
- [ ] Refactor routes to call `AuthService` instead of local helpers.
- [ ] Add unit tests asserting no session is created outside `AuthService`.

### Session Model Implementation

- [ ] Define `Session` type with:
  - `session_id`, `subject_ids`, `device_id`, `roles`, `scopes`.
  - `issued_at`, `expires_at`, `refresh_index`.
  - Placeholders: `mfa_level`, `device_trust_level`.
- [ ] Implement deterministic `session_id` generator (counter + node seed + wallet hash).
- [ ] Store sessions in a single `SessionStore` abstraction (append-only friendly).

### EvidenceBus Integration for Auth

- [ ] Define event payloads for:
  - `SESSION_CREATED`, `SESSION_REFRESHED`, `SESSION_REVOKED`.
- [ ] Implement `EvidenceBusAdapter` inside `AuthService` to emit these events.
- [ ] Add replay tests that reconstruct session state from an event stream.

### Device Hash v0 (Structure Only)

- [ ] Implement `computeDeviceHash()` (coarse, deterministic).
- [ ] Include `device_id` in the `Session` object and PoE events.
- [ ] Do not yet enforce any policy beyond storing it.

### MOCKPQC Record Scaffolding

- [ ] Define `MockPQCKey` type with `key_id`, `public_stub`, `derivation_seed_ref`.
- [ ] Add storage for per-account PQC records.
- [ ] Wire MOCKPQC subject into `Session.subject_ids` (no real crypto yet).

---

## Phase v19 – OIDC & Identity Linking

**Goal:** Add optional OIDC identities and unify subjects while keeping wallet as the only authority.

### OIDC Client Plumbing

- [ ] Add OIDC client configuration (GitHub first; PKCE required).
- [ ] Implement backend endpoints:
  - `/auth/oidc/init` → build deterministic `state` and `code_verifier`.
  - `/auth/oidc/callback` → verify code, tokens, and OIDC `id_token`.
- [ ] Ensure all OIDC flows are initiated from Electron main process (no secrets in renderer).

### Identity Binding Model

- [ ] Implement “bind OIDC to wallet” flow:
  - Generate deterministic binding message.
  - Wallet signs binding.
  - Store binding mapping `(wallet, oidc_sub)` and emit `IDENTITY_BOUND` event.
- [ ] Ensure unbound OIDC accounts have zero protocol authority.

### Unified Subject Handling

- [ ] Extend `Session` to structured subjects:
  - `subjects.wallet`, `subjects.oidc`, `subjects.mockpqc`.
- [ ] Update `AuthService`:
  - `resolveSubjectIdentity()` → wallet + pqc only.
  - `resolveTrustContext()` → add OIDC as advisory context.

### EvidenceBus for OIDC

- [ ] Add events: `OIDC_INIT`, `OIDC_CALLBACK`, `OIDC_TOKEN_VERIFIED`.
- [ ] Write replay tests that reconstruct binding state solely from EvidenceBus.

---

## Phase v20 – MFA, Device Binding v1, IPC Hardening (Live)

**Goal:** Enrich sessions with MFA/device trust, lock Electron IPC, and freeze v20 schemas/authority doctrine.

### Schema & Authority Freezing

- [ ] Add `session_schema_version = 1` to all sessions.
- [ ] Add `auth_event_version = 1` to all auth-related EvidenceBus events.
- [ ] Document authority hierarchy:
  - Level 0: wallet + PQC signatures.
  - Level 1: session state from EvidenceBus.
  - Level 2: device + MFA + OIDC advisory trust.
- [ ] Implement `resolveSubjectIdentity()` and `resolveTrustContext()` in `AuthService`.
- [ ] Require all guarded APIs to use both.

### Device Binding v1 (Soft Policy)

- [ ] Finalize `computeDeviceHash()` (Deterministic, coarse, low-entropy, logged).
- [ ] Bind refresh tokens to `device_hash` in `SessionStore`.
- [ ] On mismatch:
  - Downgrade scopes (configurable).
  - Emit `DEVICE_MISMATCH` event.
- [ ] Add tests for device change behavior and replay equivalence.

### MOCKPQC Slot Completion

- [ ] Ensure every account can have a `MockPQCKey`.
- [ ] Ensure sessions have a slot for PQC identity.
- [ ] Implement stub “sign/verify” APIs using deterministic hashes.
- [ ] Log PQC-related actions (key creation, binding) to EvidenceBus.

### MFAService (Capability, Not Hard Policy)

- [ ] Implement `MFAService`:
  - TOTP secret derivation from deterministic, logged seeds.
  - CRUD: enable, disable, verify TOTP.
- [ ] Extend `Session` with `mfa_level` and `mfa_last_verified_at`.
- [ ] Ensure MFA can be triggered (e.g., for device rebind, high-risk actions).
- [ ] Ensure MFA attempts are logged, but wallet login is not globally hard-gated.

### Electron IPC Hardening

- [ ] Enforce `contextIsolation: true`, `nodeIntegration: false`, no `remote` in all windows.
- [ ] Define a minimal IPC contract: `auth:getSession`, `auth:refresh`, `auth:biometricUnlock`.
- [ ] Keep refresh tokens and PQC private material strictly in main process / OS keychain.
- [ ] Sign or MAC sensitive IPC payloads; reject and log invalid messages.

### Biometric Unlock (Optional)

- [ ] Integrate OS biometrics to unlock local secret vault.
- [ ] On success: decrypt tokens/keys in main process only.
- [ ] Emit `BIOMETRIC_UNLOCK` events (success/fail, no biometric data).
- [ ] Tests: No secret ever accessible from renderer memory/dumps.

### “Deferred Features” Guards

- [ ] Add explicit flags/config for:
  - Offline queue disabled.
  - Consensus/Raft logic disabled.
- [ ] Ensure no code path tries to perform:
  - Offline action queuing.
  - Automatic offline replay.
  - Leader election or quorum checks.

---

## Phase v21 – Offline & Replicated Sessions

**Goal:** Add deterministic offline semantics and a replication-ready `SessionStore` while reusing all v20 structures.

### Offline Session & Counter Model

- [ ] Extend `Session` with offline-safe counters (Local operation counter / Lamport-style `local_seq`).
- [ ] Implement offline access token caching (Strict deterministic max offline duration).
- [ ] Add EvidenceBus support for delayed `SESSION_REFRESHED` / `SESSION_REVOKED` events.

### Offline Action Queue

- [ ] Implement client-side queue (Action, session_id, local_seq, device_id, signatures).
- [ ] Backend replay: Verify order, signatures, and counters.
- [ ] Append actions as PoE events preserving local order.
- [ ] Add replay tests: Construct offline logs, then reconnect and verify final state equals live-run equivalent.

### SessionStore Replication Surface

- [ ] Refine `SessionStore` API to look Raft/BFT-ready (`append`, `getById`, `scan`).
- [ ] Correlate each session mutation with EvidenceBus PoE ID.
- [ ] Implement local append-only storage engine (file/DB) that preserves total ordering.

### Trust & Policy Use of Offline Context

- [ ] Extend `resolveTrustContext()` to account for offline window size.
- [ ] Mark sessions as `offline_degraded` when near/over limits.
- [ ] Define policies for actions allowed offline and those requiring reconnection.
- [ ] Plan MFA re-verification on reconnect.

### Documentation & Doctrine

- [ ] Add a v21 “Offline & Session Replication Doctrine” doc.
- [ ] Define exact offline guarantees and non-guarantees.
- [ ] Document how EvidenceBus + SessionStore combine for full reconstruction.
