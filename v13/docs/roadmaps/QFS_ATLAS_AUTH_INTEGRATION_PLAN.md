# QFS × ATLAS — AUTH INTEGRATION ALIGNMENT (v20 LIVE BUILD)

**Context:**
v20 work is active (Electron hardening, social layer maturity, PoE rigor).
We must finish v20 without contaminating replay, while still making v21 inevitable instead of aspirational.

This document answers three questions:

1. **What from v18–v19 must already exist implicitly in v20?**
2. **What must be explicitly implemented now in v20?**
3. **What must be deliberately deferred so v21 stays clean?**

---

## 1. What Must Already Exist (Even If Not “Feature-Complete”)

These are structural commitments, not user-facing features. If these are missing, v21 becomes a refactor instead of an extension.

### 1.1 AuthService as a Facade (MANDATORY IN v20)

Even if named differently, v20 must already have a single orchestration boundary where:

* Wallet verification
* Session issuance
* EvidenceBus logging
**converge.**

If auth logic is still scattered (backend routes, Electron IPC handlers, wallet verification helpers), then v20 **must consolidate**, even if behavior is unchanged.

**Rule:**
From v20 onward, no code path creates or mutates a session outside `AuthService`.
This is the most important v18→v20 carryover.

### 1.2 Session as a First-Class Object (MANDATORY)

Even if MFA / offline is not live yet, v20 sessions must already include:

* `deterministic session_id`
* `device_id` (even if trust is “unknown”)
* `issued_at`, `expires_at`
* **Placeholder fields:**
  * `mfa_level`
  * `device_trust_level`
  * `refresh_index`

They may be inert, but they must exist so:

1. EvidenceBus schema stabilizes.
2. Replay doesn’t change later.

If you add these in v21, you break historical equivalence.

### 1.3 EvidenceBus Owns Auth Truth (ALREADY CORRECT, MUST CONTINUE)

From recent Transmissions, this is already aligned, but it must be explicit:

* **Auth is not “stateful logic”**
* **Auth is PoE-driven state reconstruction**

In v20, the following events must already exist even if revocation is manual or rare:

* `SESSION_CREATED`
* `SESSION_REFRESHED`
* `SESSION_REVOKED`

### 1.4 Make the Session / EvidenceBus Contract Explicitly Versioned

Right now "session as first-class" and "EvidenceBus owns truth" are requirements, but we must state how schema evolution is frozen for v20.

**Add in v20:**

* **Session schema versioning**
  * Include a `session_schema_version` (e.g., `1`) in every session object.
  * **Freeze the exact v20 fields:** `session_id`, `subject_ids` (wallet + pqc slot + optional oidc slot), `device_id`, `roles`, `scopes`, `issued_at`, `expires_at`, `refresh_index`, `mfa_level`, `device_trust_level`.
  * **Doctrine:** “New fields in v21+ MUST be additive and MUST NOT change semantics of v20 fields.”

* **EvidenceBus event versioning**
  * Add `auth_event_version` to `SESSION_CREATED` / `REFRESHED` / `REVOKED` / `DEVICE_MISMATCH` events.
  * Document v20 as **“Auth Event v1”** and commit to:
    * No field renames.
    * No type changes.
    * Only additive fields in later versions.

Without these explicit version tags, you risk subtle semantic shifts in v21 that break strict replay.

### 1.5 Formal “Source of Authority” Doctrine for Auth Decisions

v20 must **codify** which signals are *authoritative* and which are merely *advisory*, so v21’s extra layers (offline, Raft, stricter policies) do not re-interpret past events.

**Add in v20:**

* **Authority hierarchy (documented + enforced)**
  * **Level 0:** Wallet signatures (and, later, PQC signatures) = **ultimate authority** for identity.
  * **Level 1:** Session state reconstructed from EvidenceBus.
  * **Level 2:** Device binding, MFA status, OIDC, heuristics = **advisory modifiers** on what actions are allowed, never on who the subject is.

* **Non‑negotiable rules**
  * No event in EvidenceBus may “change” who a session belongs to; it can only:
    * Bind additional identities.
    * Change trust level / allowed scopes.
  * OIDC, device fingerprint, MFA result **cannot reassign** a wallet; they only gate capabilities.

* **Implementation hooks in v20**
  * In `AuthService`, centralize:
    * `resolveSubjectIdentity()` (wallet + PQC only).
    * `resolveTrustContext()` (device, MFA, OIDC, etc.).
  * All API guards in v20 must call both:
    * Identity resolution (authoritative).
    * Trust resolution (advisory), and log both decisions to EvidenceBus.

Without this doctrine in v20, v21 features can accidentally start treating advisory signals as authoritative.

---

## 2. What MUST Be Explicitly Implemented in v20 (No Delay)

These are the irreversible commitments that must land now, while still ALPHA-safe.

### 2.1 Device Binding v1 (Soft, Deterministic, Logged)

v20 must compute and store a `device_hash`:

* Coarse
* Low entropy
* Deterministic
* Logged to EvidenceBus

**Policy:** Can stay permissive, but:

* Refresh tokens must already be associated with a device.
* Mismatch must emit `DEVICE_MISMATCH`.

This ensures:

* MFA in v20 has a trigger.
* Offline semantics in v21 have an anchor.

### 2.2 MOCKPQC Slots Must Exist (Even If Useless)

v20 must include:

* A per-account PQC record (even if stubbed).
* A `key_id`.
* A deterministic derivation reference.

**It is fine if:**

* Signatures are hashes.
* No real cryptography happens.

**It is not fine if:**

* The session model has nowhere to put PQC identity.

This is how you avoid a breaking change later.

### 2.3 Electron IPC Hardening (This Is the Right Time)

From what you are pushing now, this is already underway. The non-negotiables for v20:

**Renderer never touches:**

* Refresh tokens.
* PQC private material.

**Renderer only asks for:**

* “Give me a session”
* “Refresh session”
* “Unlock secrets”

This matches Transmissions 9–11 directionally and must be locked now.

---

## 3. What Must Be DELIBERATELY Deferred (Do Not Implement Yet)

These are v21 responsibilities. Implementing them early will harm determinism or overcomplicate ALPHA.

### 3.1 Do NOT Enforce Hard MFA Everywhere Yet

In v20:

* MFA exists
* MFA can be triggered
* MFA is logged

But:

* **Wallet login should not always require it.**
* **Offline flows must not depend on it yet.**

Treat MFA as capability, not policy in v20.

### 3.2 Do NOT Introduce Real Offline Execution Yet

v20 should:

* Tolerate short disconnects.
* Cache access tokens.

But **do not yet**:

* Queue signed offline actions.
* Replay them automatically.

Just ensure:

* Session model supports counters.
* EvidenceBus can accept delayed events.

Full offline semantics belong to v21.

### 3.3 Do NOT Finalize Consensus/Raft Code Yet

v20 should:

* Shape `SessionStore` as append-only.
* Keep APIs consensus-friendly.

But:

* **No leader election.**
* **No quorum logic.**
* **No validator enforcement yet.**

Otherwise you risk locking wrong assumptions.

---

## 4. Transmission Alignment (8 → 11)

From the Patreon Transmissions:

* **Transmission 8–9:** “Social layer hardened, PoE first, deterministic UX” → aligns with session-as-evidence.
* **Transmission 10:** “From engine to live pipeline” → this is exactly where `AuthService` belongs.
* **Transmission 11:** “Validator / trust surfaces emerging” → impossible without v20 session enrichment.

**In other words:** The auth roadmap is not separate from Transmissions — it is the spine that makes them coherent.

---

## 5. One-Line Executive Check (v20 Readiness)

You are on track if and only if the following statement is already true in code:

> “Every authenticated action in QFS × ATLAS can be replayed from EvidenceBus and deterministically reconstructed into the same session, device, and trust context—even if MFA and offline features are not yet enforced.”

* **If yes** → v21 is additive.
* **If no** → fix now, not later.

---

## 6. What I Recommend Next (Concrete Options)

Options for immediate next steps:

1. **Audit-style checklist:** “Search your repo for X; if found, refactor to Y” (file-level guidance).
2. **Session schema + EvidenceBus diff:** Exact structs/events you should freeze in v20.
3. **Electron IPC contract spec:** One-page spec you can paste into the repo as doctrine.
4. **v21 offline flow pseudo-code:** So v20 decisions don’t block it.
