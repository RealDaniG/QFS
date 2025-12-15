# QFS × ATLAS: Appeals Workflow Specification

**Version:** 1.0
**Status:** DRAFT
**Scope:** P0 (Gap Analysis)

## 1. Purpose & Scope

The Appeals Workflow enables users to challenge moderation decisions, AEGIS flags, or policy violations in a transparent, deterministic, and ledger-backed manner.

**Core Philosophy:** Every moderation action must be **explainable**, **appealable**, and **auditable**.

## 2. Functional Requirements

### 2.1 Appeal Triggers

Users can appeal:

- Content removal/flagging
- Account restrictions (coherence penalties)
- Treasury/staking rejections
- Guild membership denials

### 2.2 Appeal Process

1. **Submit Appeal**: User provides context and evidence hash.
2. **AEGIS Review**: Automated re-evaluation with updated context.
3. **Human Review** (Optional): If AEGIS remains inconclusive, escalate to Council.
4. **Resolution**: Accept (reversal) or Reject (upheld).
5. **Ledger Record**: All steps logged to QFS Ledger.

### 2.3 Governance

- **Appeal Council**: Multi-sig group elected/rotated by governance.
- **Evidence**: All appeals must reference immutable content (IPFS CID).
- **Timeline**: 72-hour SLA for initial review.

## 3. Data Models

### 3.1 Appeal Event (On-Ledger)

```json
{
  "event_type": "APPEAL_SUBMITTED",
  "user_id": "0x...",
  "target_event_id": "ledger_event_123",
  "evidence_cid": "ipfs://Qm...",
  "reason": "False positive",
  "timestamp": "iso8601"
}
```

### 3.2 Resolution Event

```json
{
  "event_type": "APPEAL_RESOLVED",
  "appeal_id": "appeal_456",
  "decision": "ACCEPTED | REJECTED",
  "reviewer": "0xCouncil...",
  "explanation_cid": "ipfs://Qm..."
}
```

## 4. Implementation Plan

- [ ] **Phase 1**: Appeal submission API and ledger integration.
- [ ] **Phase 2**: AEGIS re-evaluation hook.
- [ ] **Phase 3**: Council dashboard (UI).
- [ ] **Phase 4**: Notification system for resolution.
