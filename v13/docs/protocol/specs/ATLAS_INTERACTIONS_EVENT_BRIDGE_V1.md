# ATLAS Interactions Event Bridge Specification v1

**Version:** 1.0  
**Date:** 2025-12-13  
**Status:** IMPLEMENTED

---

## Overview

This document defines the QFS Event Bridge for Social Interactions that routes all user actions through the deterministic QFS modules and records them in the auditable ledger with integrated guard evaluations.

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

## Error Response Format

When errors occur, the API will return a deterministic error response:

```json
{
  "error_code": "string",
  "message": "string",
  "details": "string"
}
```

### Common Error Cases

| Error Code | Conditions | Example Details |
|------------|------------|-----------------|
| `MISSING_USER_ID` | user_id parameter is missing or empty | "User ID is required for interaction requests" |
| `MISSING_TARGET_ID` | target_id parameter is missing or empty | "Target ID is required for interaction requests" |
| `INVALID_INTERACTION_TYPE` | type parameter is not one of the valid types | "Interaction type must be one of: like, comment, repost, follow, report" |
| `MISSING_CONTENT` | content parameter missing for comment interactions | "Content is required for comment interactions" |
| `MISSING_REASON` | reason parameter missing for report interactions | "Reason is required for report interactions" |
| `INTERNAL_ERROR` | Unexpected server error | "An internal error occurred" |

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
- Uses real content text for meaningful evaluation

### Economics Guard
- Validates reward calculations and token allocations
- Ensures compliance with constitutional bounds
- Returns reward estimates with explanations
- Uses realistic parameters derived from token bundle

---

## Integration Points

1. **EventEmitter**: All interactions route through the existing EventEmitter mechanism
2. **CoherenceLedger**: Events are recorded with deterministic serialization
3. **TreasuryEngine**: Reward calculations are performed for qualifying interactions
4. **Guard Evaluation**: Safety and Economics guards are invoked for each interaction
5. **AEGIS Guard**: Meta-guard orchestrator coordinates guard evaluations
6. **NotificationService**: Processes ledger entries to generate notifications

---

## Implementation Details

### AtlasAPIGateway.post_interaction Method
Located in `src/atlas_api/gateway.py`

Process:
1. Validate request shape
2. Get deterministic timestamp from DRV packet
3. Create canonical interaction event structure
4. Generate deterministic event ID
5. Get real token bundle for the user
6. Build HSMF metrics from interaction data
7. Emit ledger event via CoherenceLedger with real HSMF metrics
8. Process with AEGIS Guard in observation mode
9. Process notification via NotificationService
10. Build realistic economic parameters from token bundle and interaction
11. Calculate estimated reward amount based on interaction type
12. Invoke EconomicsGuard with realistic parameters
13. Create guard results from AEGIS observation
14. Compute reward estimate via TreasuryEngine (simulation-style call)
15. Return response with success determined by guard results

### Guard Results Integration
- `safety_guard_passed`: Derived from AEGIS observation's safety guard result
- `economics_guard_passed`: Derived from AEGIS observation's economics guard result
- `explanation`: Combined explanation from both guard results

### HSMF Metrics Generation
- Extracts relevant metrics from token bundle
- Adjusts metrics based on interaction type
- Provides real HSMF metrics to TreasuryEngine for reward calculation