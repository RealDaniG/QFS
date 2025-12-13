# ATLAS Interactions Event Bridge Specification v1

**Version:** 1.0  
**Date:** 2025-12-13  
**Status:** DRAFT

---

## Overview

This document defines the QFS Event Bridge for Social Interactions that routes all user actions through the deterministic QFS modules and records them in the auditable ledger.

---

## Endpoint

`POST /api/v1/interactions/{type}`

Where `{type}` can be:
- `like`
- `comment`
- `repost`
- `follow`
- `report`

---

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user identifier |
| `target_id` | string | Yes | Target entity identifier (post, user, etc.) |
| `content` | string | Conditional | Comment content (required for comment type) |
| `reason` | string | Conditional | Report reason (required for report type) |

---

## Response Format

```json
{
  "success": "boolean",
  "event_id": "string",
  "guard_results": {
    "safety_guard_passed": "boolean",
    "economics_guard_passed": "boolean",
    "explanation": "string"
  },
  "reward_estimate": {
    "amount": "BigNum128",
    "token_type": "string",
    "explanation": "string"
  }
}
```

---

## Ledger/Event Requirements

Each interaction generates exactly one canonical ledger event with:

1. **EventType**: Corresponds to interaction type
2. **Timestamp**: Deterministic event sequence number
3. **Modules**: References to involved modules (CoherenceEngine, TreasuryEngine, etc.)
4. **Inputs**: Original request parameters
5. **Guards**: Results from SafetyGuard and EconomicsGuard evaluations
6. **Outcome**: Success/failure status
7. **Explanation**: Human-readable description
8. **Version**: Schema version for backward compatibility

---

## Guard Expectations

### Safety Guard
- Evaluates content safety for comments and reports
- Checks against policy-defined safety thresholds
- Returns structured result with explanation

### Economics Guard
- Validates reward calculations and token allocations
- Ensures compliance with constitutional bounds
- Returns reward estimates with explanations

---

## Integration Points

1. **EventEmitter**: All interactions route through the existing EventEmitter mechanism
2. **CoherenceLedger**: Events are recorded with deterministic serialization
3. **TreasuryEngine**: Reward calculations are performed for qualifying interactions
4. **Guard Evaluation**: Safety and Economics guards are invoked for each interaction

---