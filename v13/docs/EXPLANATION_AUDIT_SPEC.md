# Explanation Audit Specification

**Version:** 1.0
**Date:** 2025-12-14
**Status:** DRAFT

## 1. Overview

The Explanation Audit system provides a transparent, verifiable, and immutable record of all algorithmic decisions made by the QFS Value Node. It allows users and auditors to:

1. View detailed breakdowns of rewards and rankings.
2. Verify the integrity of these decisions against the immutable QFS ledger.
3. Audit the specific policy versions and logic used at the time of decision.

## 2. API Schema

### 2.1 Retrieve Explanation

`GET /api/v1/audit/explanation/{event_id}`

**Response:**

```json
{
  "event_id": "string",
  "category": "REWARD | RANKING",
  "timestamp": "iso8601",
  "explanation": {
    "summary": "string",
    "breakdown": {
      "base": "amount",
      "bonuses": [{"label": "string", "amount": "amount"}],
      "caps": [{"label": "string", "amount": "amount"}]
    },
    "policy_context": {
      "humor_version": "string",
      "artistic_version": "string",
      "global_hash": "sha256"
    },
    "zero_sim_proof": {
      "input_hash": "sha256",
      "logic_hash": "sha256",
      "output_hash": "sha256"
    }
  }
}
```

### 2.2 Verify Explanation

`POST /api/v1/audit/verify`

**Request:**

```json
{
  "explanation_blob": "json_object"
}
```

**Response:**

```json
{
  "verified": true,
  "reproduced_hash": "sha256",
  "status": "PASS | FAIL"
}
```

## 3. Frontend Component (`ExplanationAuditPanel`)

- **Input:** `explanationId` or `eventObject`.
- **Display:**
  - **Summary Card:** High-level result (e.g., "+50 ATR").
  - **Waterfall Chart:** Visualization of Base -> Bonuses -> Caps -> Final.
  - **Policy Badge:** Shows active policies (Humor v1, Artistic v1).
  - **Verify Button:** Triggers client-side hash verification or server-side replay.

## 4. Zero-Sim Compliance

- All audit data is derived *exclusively* from the ledger.
- No "audit logs" are stored separately; they are reconstructed on-demand from the immutable event stream (Event Sourcing).
