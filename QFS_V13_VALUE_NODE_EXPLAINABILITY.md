# QFS V13.8 Value-Node Explainability Specification

## 1. Overview

This specification defines the "Value-Node / User-as-Token" interpretation layer for QFS V13. It ensures that a user's economic state is fully deterministically reconstructible from the ledger, and provides a "Explain-This" capability to surface these mechanics to the user without exposing the core economic engines.

## 2. Hard Requirements

- **Determinism**: Output must be identical for the same ledger history, regardless of time or platform.
- **Zero-Simulation**: No floating point, no randomness, no wall-clock time in logic.
- **Read-Only**: The explanation layer MUST NOT mutate any state, balances, or rewards.
- **Isolation**: No direct access to `TreasuryEngine` or `RealLedger` for the explanation generation. It must rely on replayed events.

## 3. Architecture

### 3.1. Data Flow

```mermaid
graph TD
    Ledger[Ledger Events] -->|Replay| ValueGraphRef[ValueGraphRef (In-Memory)]
    ValueGraphRef -->|State| ExplainHelper[ValueNodeExplainabilityHelper]
    ExplainHelper -->|Explanation Object| API[ATLAS API]
    API -->|JSON| Frontend[ATLAS UI (ExplainThisPanel)]
```

### 3.2. Components

1. **ValueGraphRef (`v13/ATLAS/src/value_graph_ref.py`)**:
    - Ingests linear history of events.
    - Reconstructs UserNode and ContentNode state.
    - Maintains interaction and reward edges.

2. **ValueNodeExplainabilityHelper (`v13/policy/value_node_explainability.py`)**:
    - Takes *Event Context* and *Replayed State*.
    - Generates `ValueNodeRewardExplanation` structure.
    - Hashing: Generates SHA-256 hash of the explanation for verification.

3. **Frontend Integration (`v13/ATLAS/src/lib/qfs/explain-this.ts`)**:
    - TypeScript interfaces mirroring the backend explanation objects.
    - No logic, just display and type validation.

## 4. Invariants

1. **Replay Consistency**: `Replay(History)` == `Live_State`
2. **Explanation Determinism**: `Explain(State, Event)` -> `Constant_Hash`
3. **No Mutation**: Explanation generation has 0 side effects.

## 5. Schema

The explanation object schema involves:

- `summary`: Plain text summary.
- `reason_codes`: Machine-readable codes (e.g., `REWARD_BONUS`, `GUARD_LIMIT`).
- `breakdown`: Detailed math (simplified for display).
- `policy_info`: Version and Hash of the policy used.

## 6. Verification

- **Unit Tests**: Verify helper output against known inputs.
- **Replay Tests**: streaming events -> verify final state matches snapshot.
- **Fuzzing**: Feed random event streams, ensure no crashes and deterministic output.
