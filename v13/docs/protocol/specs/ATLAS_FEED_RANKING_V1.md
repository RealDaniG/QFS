# ATLAS Feed Ranking Specification v1

**Version:** 1.0  
**Date:** 2025-12-13  
**Status:** IMPLEMENTED

---

## Overview

This document defines the Coherence-Based Feed Ranking API that integrates the QFS CoherenceEngine with the frontend to provide deterministic, policy-aware content ranking with integrated safety checks.

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
| `MISSING_USER_ID` | user_id parameter is missing or empty | "User ID is required" |
| `INVALID_LIMIT` | limit parameter is not between 1-100 | "Limit must be between 1 and 100" |
| `INVALID_MODE` | mode parameter is not 'coherence' or 'chronological' | "Mode must be either 'coherence' or 'chronological'" |
| `INTERNAL_ERROR` | Unexpected server error | "An internal error occurred" |

---

## Integration with CoherenceEngine

The feed endpoint integrates with the existing `CoherenceEngine.py` module:

1. **Content Candidate Retrieval**: Fetches real content candidates from storage/IPFS with actual content text
2. **Coherence Input Building**: Constructs CoherenceInput including content text for safety checks
3. **Feature Vector Construction**: Builds feature vectors from engagement signals
4. **Ranking Computation**: `CoherenceEngine.rank_content()` is called with deterministic parameters
5. **Safety Guard Integration**: Content text is passed to AEGIS/SafetyGuard for evaluation
6. **Policy Alignment**: Results include policy version for auditability
7. **Determinism Guarantee**: Same inputs always produce identical ranked results

---

## Safety Checks

### Content Safety Evaluation
- Uses real content text for meaningful safety validation
- Evaluates against safety policies using deterministic models
- Generates risk scores for content classification
- Flags content with risk scores above threshold (0.5)

### Safety Guard Integration
- Integrated with AEGIS Guard for observation-only evaluation
- Processes feed ranking events with content text
- Returns structured results with risk scores and explanations

---

## Determinism Constraints

- All timestamps use block height or event sequence numbers, not wall-clock time
- Ranking algorithm uses only CertifiedMath functions
- No randomization or external API calls in ranking computation
- All intermediate states are deterministic
- Content candidates include actual text for meaningful safety checks

---

## Implementation Details

### AtlasAPIGateway.get_feed Method
Located in `src/atlas_api/gateway.py`

Process:
1. Validate request shape
2. Get deterministic timestamp from DRV packet
3. Fetch real content candidates with actual content text
4. Create engagement signal vector (I_vector)
5. For each candidate:
   - Build CoherenceInput including content text
   - Build feature vector from CoherenceInput
   - Update omega using CoherenceEngine
   - Calculate coherence score
   - Process with AEGIS Guard for feed ranking
6. Sort posts by coherence score
7. Apply limit and return response

### Content Candidate Structure
```python
{
    "content_id": str,              # Unique content identifier
    "author_did": str,              # Author's decentralized identifier
    "community_id": str,            # Community identifier
    "tags": List[str],              # Content tags
    "engagement_signals": Dict,     # Engagement metrics (likes, comments, shares)
    "content_cid": str,             # IPFS content identifier
    "created_at": int,              # Creation timestamp
    "content_type": str,            # Type of content
    "content": str                  # Actual content text for safety checks
}
```