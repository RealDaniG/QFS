# Layer D: Agent Advisory (Phase 2) Implementation Status

**Status:** Deployed to Dev (Simulated)
**Branch:** `feat/v17-layer-d-advisory-signals`

## Components Implemented

### 1. Backend Adapters (`v17/agents/`)

- **Schema:** `AdvisorySignal` (Target ID, Score, Reasons, Model Version).
- **Governance:** `AGENT_ADVISORY_PROPOSAL` (Heuristics: Amount, Description Length).
- **Bounties:** `AGENT_ADVISORY_BOUNTY` (Heuristics: References, Content Length).
- **Social:** `AGENT_ADVISORY_SOCIAL` (Heuristics: Keywords "scam", "fraud").
- **Listener:** `AdvisoryListener` to consume events and emit signals.

### 2. UI Projections (`v17/ui/`)

- **Governance:** Overlays advisory signals onto Proposal DTOs.
- **Bounty:** Injects "Agent Suggestion" stages into Bounty Timelines.
- **Social:** Attaches signals to Threads for "Needs Review" indicators.

## Verification

- **Unit Tests:** `v17/tests/test_advisory_f_layer.py` (Pass)
- **UI Tests:** `v17/tests/test_ui_advisory.py` (Pass)
- **Smoke Test:** `scripts/smoke_test_layer_d.py` (Success)
- **Zero-Simulation:** Compliant (Deterministic inputs, Timestamp propagation).

## Next Steps

- Implement advanced models (Tier 2) using LLM calls (wrapped in deterministic cache).
- Add "Explanation" feature (why did the agent flag this?).
- Integrate with `AdvisoryRouter` in v18 for multi-agent consensus.
