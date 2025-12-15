# QFS × ATLAS: Explain-This System Specification

**Version:** 1.0
**Status:** DRAFT
**Scope:** P0 (Gap Analysis)

## 1. Purpose & Scope

The **Explain-This** system provides transparent, deterministic, and auditable explanations for **any** QFS or ATLAS decision, including:

- Reward calculations
- Coherence score changes
- Content ranking decisions
- AEGIS advisory flags
- Treasury allocations
- Policy enforcement actions

**Core Philosophy:** Every algorithmic decision must be **explainable** from **ledger events** alone.

## 2. Zero-Simulation Contract

1. **Ledger-Derived**: All explanations must be reproducible from the immutable event ledger.
2. **No Off-Ledger Secrets**: Explanation inputs cannot include hidden state.
3. **Deterministic**: Same ledger state → Same explanation.
4. **Versioned**: Explanation logic is versioned and pinned to specific ledger epochs.

## 3. Functional Requirements

### 3.1 Explainable Entities

- **Rewards**: Why amount X was awarded.
- **Coherence**: Why score changed from A to B.
- **Rankings**: Why content C ranked above D.
- **Flags**: Why AEGIS flagged content E.
- **Rejections**: Why action F was blocked by policy.

### 3.2 Explanation Structure

Every explanation contains:

- **Target**: What is being explained (event ID, user action).
- **Inputs**: Ledger events that contributed to the decision.
- **Logic**: Reference to the policy/algorithm version used.
- **Output**: The computed result.
- **Proof Hash**: Cryptographic proof of derivation.

### 3.3 User Experience

- **UI Button**: "Explain This" next to any decision.
- **Drill-Down**: Click input events to recursively explain them.
- **Export**: Download explanation as JSON for external audit.

## 4. Data Models

### 4.1 Explanation Object

```json
{
  "id": "explain_abc123",
  "target_type": "REWARD",
  "target_id": "reward_event_456",
  "inputs": [
    {"event_id": "content_posted_789", "weight": 0.6},
    {"event_id": "user_coherence_updated_101", "weight": 0.4}
  ],
  "policy_version": "v13.8.2",
  "computation": {
    "base_reward": 100,
    "coherence_multiplier": 1.2,
    "final_reward": 120
  },
  "proof_hash": "sha256...",
  "generated_at": "iso8601"
}
```

### 4.2 Ledger Integration

Explanations are **not** stored in the primary ledger but are generated on-demand from it.
They can be cached in a **read-only** explanation index for performance.

## 5. Implementation Plan

- [ ] **Phase 1**: Core Explainer Engine (`v13.services.explainer/`).
- [ ] **Phase 2**: Integration with existing observatories (Humor, Artistic, Value Node).
- [ ] **Phase 3**: REST API for on-demand explanations.
- [ ] **Phase 4**: UI integration with drill-down navigation.

## 6. Security Considerations

- **PII Leakage**: Explanations must not expose private user data.
- **Algorithm Disclosure**: Policy details are public by design (governance principle).
- **Proof Verification**: Users can verify proof hashes against published policy code.

## 7. Success Metrics

- 100% of reward events explainable.
- Explanation generation < 500ms for 95th percentile.
- Zero contradictions between explanation and ledger state.
