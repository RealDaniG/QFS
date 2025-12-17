# ATLAS 1.2 — Deterministic Session Management

> **Current Status:** ATLAS 1.2 Released (Session Management & Explainability)  
> **Backend:** QFS V18.9 (Deterministic Session Management)  
> **Frontend:** Next.js 15 + Explain-This Panels

ATLAS 1.2 transforms ATLAS × QFS into a **deterministic, two-sided "Explain-This" platform**: users and operators can inspect **why** value, rewards, rankings, and visibility occur, while all real economics remain exclusively governed by QFS.

ATLAS is now formally constrained to act as a **read-only projection and intent router**, never an economic authority.

---

## What ATLAS 1.2 Delivers

### 1. Deterministic Platform Architecture

ATLAS is explicitly defined as:

- A **deterministic view layer** over QFS.
- An **intent submission layer** for governance and policy.
- PostgreSQL/Prisma are locked to **non-authoritative roles only** (sessions, UI prefs, drafts, caches).

**CI Enforcement Blocks:**

- Forbidden economic imports.
- Direct balance/reward mutation.
- Accidental economic fields in UI schemas.

**AI Constraint:**

- AI is **advisory only**; all real effects flow:
  `observation → policy → governance → treasury`

**Result:** Architectural guarantees are enforced by tooling, not trust.

### 2. Deterministic Session Management System

`SessionManager` is fully production-grade:

- **Deterministic authentication** with challenge-response flow.
- **Ledger-replayable** session state reconstruction.
- **Explain-This integration** for cryptographic proof generation.
- **Zero-Simulation compliant** with no randomness or time dependencies.

**Verification:**

- Backed by **17 tests** covering session lifecycle, rotation, revocation, and replay.
- Complete artifact set: Spec, evidence bundle, Zero-Sim status, API contracts.

**Result:** ATLAS now supports secure, deterministic session management without economic risk.

### 3. Hardened Signal System (Humor Slice)

`HumorSignalAddon` is fully production-grade:

- **Pure signal** (no economics).
- **Deterministic**, Zero-Simulation compliant.
- Policy-bounded, observable, explainable.

**Verification:**

- Backed by **40+ tests** covering edge cases, caps, malformed input, determinism, hash stability.
- Complete artifact set: Spec, evidence bundle, Zero-Sim status, ATLAS schema, roadmap links.

**Result:** ATLAS now supports governed, explainable signals without economic risk.

### 4. Deterministic Storage & Proof Replay

`StorageEngine` upgraded with:

- Fully logged deterministic `StorageEvent`s.
- Replay helpers that reconstruct state and validate hashes.

**Visibility:**

- Proofs, epochs, and storage metrics are now **Replayable**, **Auditable**, and **Viewable** without mutating economics.
- Risks and invariants are explicitly documented and tested.

**Result:** Storage behavior is inspectable and verifiable, not opaque.

### 5. Value-Node Replay & Explainability (V18.9)

Introduced **user-as-value-node** and **content-as-object** semantics as replayable views.

**Implemented Components:**

- `ValueNodeReplayEngine`
- `ValueNodeExplainabilityHelper`

**User Capabilities:**

- Users can now deterministically answer:
  - "Why does my wallet/value look like this?"
  - "Which signals contributed?"

**Explanations are:**

- Hash-stable.
- Replay-derived.
- Economically inert.

**Result:** Economic outcomes are explainable without exposing or mutating the engine.

### 6. Explain-This APIs & ATLAS UI

**Implemented Read-Only APIs:**

- `GET /explain/reward/{wallet_id}`
- `GET /explain/ranking/{content_id}`
- `POST /session/challenge` (Session challenge request)
- `POST /session/establish` (Session establishment with challenge response)
- End-to-end tested with deterministic hashes.

**Live UI Components:**

- `ExplainThisPanel`: Visualizes breakdowns (base, bonus, caps, guards).
- `ValueNodeView`: Projects total user value from ledger.
- `StorageDashboard`: Visualizes storage proofs and node health.
- `SessionManager`: Manages deterministic session lifecycle with visual indicators.

**Result:** ATLAS users can finally see **why** the system behaves as it does.

### 7. Roadmap, Evidence, and Governance Readiness

A single **canonical roadmap tracker** encodes:

- Invariants.
- Completed slices.
- Remaining work.

Every slice is backed by:

- Specs.
- Evidence JSON.
- Zero-Sim status.
- Cross-references.

**Status:** P0–P2 ATLAS deliverables are complete.

**Result:** The platform is auditable, governable, and review-ready.

---

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Production Stack

- **Frontend:** Next.js 15 (App Router), TypeScript 5, Tailwind CSS 4, shadcn/ui
- **State:** Zustand (UI only), TanStack Query (Ledger views)
- **Backend:** Axum/FastAPI (QFS), PostgreSQL (Non-authoritative metadata)
- **Auth:** NextAuth.js (Session/Wallet binding) with deterministic session management

## Powered by Z.ai

Optimized for robust AI-assisted development.