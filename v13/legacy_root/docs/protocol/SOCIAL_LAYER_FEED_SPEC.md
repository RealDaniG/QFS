# Social Layer / Feed Specification

**Version:** 1.0  
**Date:** 2025-12-13  
**Status:** IMPLEMENTED  

---

## Overview

This document defines the Coherence-Based Feed Ranking system that integrates the QFS CoherenceEngine with the ATLAS social platform to provide deterministic, policy-aware content ranking with integrated safety checks.

---

## Feed Ranking Process

### Content Candidate Retrieval
- Fetches real content candidates from storage/IPFS
- Includes actual content text for safety evaluation
- Contains metadata (author DID, community ID, tags, engagement signals)

### Coherence Input Building
- Constructs CoherenceInput from content candidates
- Includes content text for safety checks
- Contains all necessary metadata for CoherenceEngine

### Feature Vector Construction
- Builds feature vectors from CoherenceInput
- Uses engagement signals (likes, comments, shares) as features
- Feeds vectors to CoherenceEngine for ranking

### Coherence Engine Integration
- Calls CoherenceEngine.update_omega with feature vectors
- Calculates coherence scores as the norm of updated omega vectors
- Ranks posts by coherence score (descending)

### Safety Guard Integration
- Passes content text to AEGIS/SafetyGuard for safety checks
- Evaluates content against safety policies using deterministic models
- Flags unsafe content based on risk scores

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

### Coherence Input Structure
```python
{
    "content_cid": str,             # IPFS content identifier
    "author_did": str,              # Author's decentralized identifier
    "community_id": str,            # Community identifier
    "tags": List[str],              # Content tags
    "engagement_signals": Dict,     # Engagement metrics
    "created_at": int,              # Creation timestamp
    "content_type": str,            # Type of content
    "content": str                  # Actual content text for safety checks
}
```

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

## Deterministic Guarantees

- All timestamps use deterministic time from DRV packets
- Ranking algorithm uses only CertifiedMath functions
- No randomization or external API calls in ranking computation
- All intermediate states are deterministic
- Content candidates include actual text for meaningful safety checks

---

## API Endpoints

### GET /api/v1/feed
Retrieves coherence-ranked content feed.

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user identifier |
| `cursor` | string | No | Pagination cursor for next page |
| `limit` | integer | No | Number of items to return (default: 20, max: 100) |
| `mode` | string | No | Ranking mode: `coherence` (default) or `chronological` |

#### Response Format
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

## Known Limitations

### P1 Limitations
- Uses mock content candidates for demonstration
- Safety guard uses heuristic-based validation (not ML models)
- Feature vectors are simplified (engagement signals only)
- CoherenceEngine integration is basic (no advanced features)

### Future Enhancements
- Integration with real storage/IPFS for content retrieval
- Advanced ML-based safety models
- Sophisticated feature extraction algorithms
- Personalized ranking based on user preferences