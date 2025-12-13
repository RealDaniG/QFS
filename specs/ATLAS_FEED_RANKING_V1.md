# ATLAS Feed Ranking Specification v1

**Version:** 1.0  
**Date:** 2025-12-13  
**Status:** DRAFT

---

## Overview

This document defines the Coherence-Based Feed Ranking API that integrates the QFS CoherenceEngine with the frontend to provide deterministic, policy-aware content ranking.

---

## Endpoint

`GET /api/v1/feed`

---

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user identifier |
| `cursor` | string | No | Pagination cursor for next page |
| `limit` | integer | No | Number of items to return (default: 20, max: 100) |
| `mode` | string | No | Ranking mode: `coherence` (default) or `chronological` |

---

## Response Format

```json
{
  "posts": [
    {
      "post_id": "string",
      "coherence_score": "BigNum128",
      "policy_version": "string",
      "why_this_ranking": "string",
      "timestamp": "integer"
    }
  ],
  "next_cursor": "string",
  "policy_metadata": {
    "version": "string",
    "applied_at": "integer"
  }
}
```

---

## Integration with CoherenceEngine

The feed endpoint integrates with the existing `CoherenceEngine.py` module:

1. **Input Processing**: User context and preferences are converted to CoherenceEngine inputs
2. **Ranking Computation**: `CoherenceEngine.rank_content()` is called with deterministic parameters
3. **Policy Alignment**: Results include policy version for auditability
4. **Determinism Guarantee**: Same inputs always produce identical ranked results

---

## Determinism Constraints

- All timestamps use block height or event sequence numbers, not wall-clock time
- Ranking algorithm uses only CertifiedMath functions
- No randomization or external API calls in ranking computation
- All intermediate states are deterministic

---