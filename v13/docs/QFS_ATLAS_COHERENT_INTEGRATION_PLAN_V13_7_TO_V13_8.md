# QFS × ATLAS Coherent Integration Plan (V13.7 → V13.8)

## 1. Core economic source of truth

- QFS remains the **only** deterministic economic substrate; ATLAS never invents or mutates balances directly.
- All balances, rewards, and ATR/FLX flows are produced and conserved exclusively by:
  - TreasuryEngine  
  - RewardAllocator  
  - HarmonicEconomics  
  - BigNum128/CertifiedMath (no floats, no hidden rounding).
- ATLAS is a **read/write surface**:
  - Writes: user actions encoded as QFS transactions.  
  - Reads: views over QFS state and replayed histories.  
  - No direct DB writes that change token state.

## 2. Fixed harmonic token compliance

- Token universe is **closed**: only protocol‑defined tokens (ATR, FLX, NOD, governance token, etc.) exist.
- No V13.7 or V13.8 feature may:
  - Introduce a new monetary token.  
  - Mint/burn outside TreasuryEngine.  
  - Change balances without a ledger‑recorded, guard‑checked TreasuryEngine path.  
- Mint/burn rules:
  - Governed schedules and policies.  
  - Deterministic formulas, replay‑verifiable from ledger events.

## 3. V13.8: users as value nodes, content as NFTs

- **User-as-value node**:
  - Each user has a replayable `UserState` projection (balances, ATR/FLX, engagement/coherence metrics, governance footprint) built from events.
- **Content-as-NFT**:
  - Each content object has a deterministic `content_id = H(canonical(payload, metadata))` using canonical JSON + SHA‑256.
  - Content is versioned; each version is a new immutable content node.
- **Value graph** (representational layer):
  - Nodes: `UserNode(user_id)`, `ContentNode(content_id)`.  
  - Edges:
    - `InteractionEdge(user → content)` (likes, comments, shares, etc.).  
    - `RewardEdge(system → user)` optionally tagged with `content_id` and token type.  
    - `GovernanceEdge(user → proposal)` (proposals/votes).  
  - This graph:
    - Is derived from ledger events and policies.  
    - Does **not** mint tokens or directly change balances; it **explains and attributes** value flows.

## 4. Deterministic replay and Zero‑Sim

- Core requirement:
  - No randomness, wall‑clock time, or non‑deterministic I/O in economic or value‑graph construction.  
  - Any time source is a deterministic tick (block/DRV index), not system clock.
- Replay guarantees:
  - Given ordered ledger events and static policies, both:
    - Core balances.  
    - Value graph (nodes, edges, `UserState` projections)  
    can be reconstructed bit‑for‑bit.  
- Tests:
  - Existing V13.8 Phase‑0 tests already prove:
    - Content ID determinism.  
    - Value‑node replay invariance for a sample event trace.  
  - Future tests must extend this to real QFS event structures.

## 5. ATLAS responsibilities & observability

- **Explain‑This panels (V13.7+)**:
  - For each post or action, ATLAS can show:
    - Base reward vs signal bonuses (humor, artistic, coherence, etc.).  
    - Caps and policy limits applied.  
    - Short, policy‑derived explanations (e.g. “Humor bonus capped at 20% of base reward due to policy X”).
  - Panels are **read‑only**: they display QFS‑generated metadata, never recompute economics.
- **Signal & Value Graph Observatory (V13.8)**:
  - Governance‑facing dashboards that:
    - Visualize distributions of signals and rewards.  
    - Show value‑graph structure (who created what, how it was rewarded, how users voted).  
  - Provide **what‑if simulations**:
    - Adjust signal weights/caps in a sandbox.  
    - Recompute rewards/ranks over snapshots deterministically, without touching live state.
- ATLAS experimentation:
  - Safe by design: all simulations and visualizations are based on replay and representational models, not live treasury mutations.

## 6. Governance and policy hooks

- Any mapping from:
  - Value‑node signals, content events, or SignalAddons  
  → to rewards or rank must:
  - Be described in PolicyRegistry / policy docs.  
  - Be adopted via formal governance (proposal + vote).  
  - Preserve deterministic replay and Zero‑Sim invariants.
- SignalAddons:
  - Deterministic evaluators only (humor vectors, artistic scores, etc.).  
  - They **do not** allocate tokens; they feed into TreasuryEngine via policy weights.  
- Value‑node/content‑ID layers:
  - Classified as **observation and attribution** tooling:
    - They track how existing tokens flowed.  
    - They never introduce new instruments or bypass guards.

## 7. Concrete next steps and plan adjustments

### 7.1 Mission constraints & scope lock

- Maintain `docs/QFS_ATLAS_MISSION_CONSTRAINTS.md` as the central mission constraints doc:
  - Fixed token set, no new monetary tokens in V13.7/V13.8.  
  - All value flows via TreasuryEngine and guards.  
  - V13.8 as representational value‑graph layer.  
  - Zero‑Sim and replayability constraints for all features.  
- Keep scopes aligned:
  - `docs/QFS_V13_7_SCOPE.md`:
    - Focus on RealLedger, secure‑chat, SignalAddons, operator tools.  
    - No value‑node semantics; ATLAS‑ready stability is priority.  
  - `specs/QFS_V13_8_VALUE_NODE_MODEL.md`:
    - Focus on value‑nodes, content_id, value graph.  
    - Include clear “Non‑Goals”: no new tokens, no guard bypass, no AGI‑driven mutation.

### 7.2 Value graph formalization (V13.8)

- Extend the V13.8 spec with a **Value Graph** section:

  - Node types: `UserNode`, `ContentNode`.  
  - Edge types: `InteractionEdge`, `RewardEdge`, `GovernanceEdge`.  
  - Invariants:
    - All token‑denominated changes occur on RewardEdges via TreasuryEngine, recorded in ATR/FLX.  
    - The value graph is fully reconstructible from ledger events and policies.  
    - Graph building is side‑effect‑free and deterministic.

- Implement a pure reference helper:
  - `src/value_graph_ref.py`:
    - Ingests a small event list (ContentCreated, InteractionCreated, RewardAllocated, GovernanceVoteCast).  
    - Builds an in‑memory value graph for tests.  
    - Never touches TreasuryEngine or ledger clients.

- Extend tests:
  - `tests/value_node/test_value_graph_ref.py`:
    - Node/edge creation.  
    - Replay invariance: same event trace → identical graph.  
  - Integrate with existing `UserState` replay tests to cross‑check balances and engagement counts.

### 7.3 ATLAS value insights planning (V13.8+)

- Maintain `docs/ATLAS_UI_V13_8_VALUE_INSIGHTS.md` describing a future UI:

  - Per‑user view:
    - Content they created (content_ids).  
    - Interactions and governance actions.  
    - Associated ATR/FLX flows, derived by replay.  
  - Per‑content view:
    - Which users interacted, how it was rewarded, where it appears in governance.  
  - All explicitly **read‑only** over QFS; no state changes.

### 7.4 Policy sandbox & observatory

- Implement a **policy simulation API** (governance‑only):

  - Input: snapshot height + proposed signal weights/caps.  
  - Output: recomputed rewards/ranks and summary metrics.  
  - Must be deterministic and logged as EQM events (who simulated what, when).

- Extend Signal/Value Observatories:

  - Distribution and correlation views.  
  - Anomaly detection restricted to deterministic, threshold‑based methods.

---

**Outcome:**  
QFS stays the canonical, guard‑protected source of economic truth; ATLAS becomes
a transparent, deterministic observability and interaction surface. V13.8’s
value‑node and content‑NFT features remain representational and replay‑driven,
enriching attribution and governance without ever opening new monetary paths or
undermining harmonic token invariants.
