# Milestone: Auth Core Expansion (v18)

**Objective:** Centralize auth, formalize sessions, plug into EvidenceBus, and prepare MOCKPQC/device slots without changing UX.

## Features

- **AuthService Consolidation:** Single entry point for all auth logic.
- **Session Model:** Deterministic `session_id`, `device_id` included.
- **EvidenceBus Integration:** Auth events logged.
- **MOCKPQC Scaffolding:** Per-account PQC record structure.

## Verification

- [ ] No session created outside `AuthService`.
- [ ] Replay tests reconstruct session state from events.
